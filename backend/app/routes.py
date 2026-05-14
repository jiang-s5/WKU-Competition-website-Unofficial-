import re
from datetime import datetime
from urllib.parse import urlparse

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, init_db
from .i18n import SUPPORTED_LANGS, translate
from .seed import seed_initial_data

web = Blueprint("web", __name__)


def t(key):
    return translate(session, key)


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def is_admin(user):
    return bool(user and user["role"] == "admin")


@web.before_app_request
def bootstrap():
    init_db()
    seed_initial_data()
    lang = request.args.get("lang")
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang


@web.app_context_processor
def inject_context():
    return {
        "t": t,
        "current_lang": session.get("lang", "zh"),
        "supported_langs": SUPPORTED_LANGS,
        "current_user": current_user(),
        "site_setting": site_setting,
    }


def auth_home_redirect(tab="login"):
    return redirect(url_for("web.home", auth=tab))


def internal_redirect(target, fallback_endpoint):
    if target:
        parsed = urlparse(target)
        if not parsed.netloc or parsed.netloc == request.host:
            safe_path = parsed.path or "/"
            if parsed.query:
                safe_path = f"{safe_path}?{parsed.query}"
            return redirect(safe_path)
    return redirect(url_for(fallback_endpoint))


def require_login():
    if not current_user():
        flash("Please log in first." if session.get("lang") == "en" else "请先登录。")
        return auth_home_redirect("login")
    return None


def require_admin():
    user = current_user()
    if not is_admin(user):
        flash(
            "Please log in with an administrator account."
            if session.get("lang") == "en"
            else "请先使用管理员账号登录。"
        )
        return redirect(url_for("web.admin_login", next=request.path))
    return None


def admin_redirect(fallback_endpoint="web.admin"):
    target = request.form.get("next") or request.args.get("next") or request.referrer
    return internal_redirect(target, fallback_endpoint)


def add_audit(action, target_type, target_id, detail=""):
    user = current_user()
    actor_id = user["id"] if user else None
    get_db().execute(
        "INSERT INTO audit_logs (actor_id, action, target_type, target_id, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (actor_id, action, target_type, str(target_id), detail, datetime.utcnow().isoformat()),
    )
    get_db().commit()


def site_setting(key, default=""):
    row = get_db().execute("SELECT value FROM site_settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_site_setting(key, value):
    get_db().execute(
        """
        INSERT INTO site_settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )
    get_db().commit()


def slugify_text(text):
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").strip().lower())
    return slug.strip("-")


def internal_phone_value(student_id):
    return f"AUTO-{(student_id or '').strip()}"


def admin_stats(db):
    return {
        "users": db.execute("SELECT COUNT(*) AS count FROM users WHERE role != 'admin'").fetchone()["count"],
        "teams": db.execute("SELECT COUNT(*) AS count FROM teams WHERE status = 'pending'").fetchone()["count"],
        "posts": db.execute("SELECT COUNT(*) AS count FROM forum_posts").fetchone()["count"],
        "feedback": db.execute("SELECT COUNT(*) AS count FROM feedback_entries WHERE status = 'new'").fetchone()["count"],
    }


def pending_teams_data(db):
    return db.execute(
        """
        SELECT teams.*, users.real_name AS captain_name, users.username AS captain_username
        FROM teams
        JOIN users ON users.id = teams.captain_id
        WHERE teams.status = 'pending'
        ORDER BY teams.created_at DESC
        """
    ).fetchall()


def feedback_items_data(db):
    return db.execute(
        """
        SELECT feedback_entries.*, users.real_name, users.username
        FROM feedback_entries
        JOIN users ON users.id = feedback_entries.user_id
        ORDER BY feedback_entries.created_at DESC
        """
    ).fetchall()


def forum_posts_data(db):
    return db.execute(
        """
        SELECT forum_posts.*, users.username
        FROM forum_posts
        JOIN users ON users.id = forum_posts.user_id
        ORDER BY forum_posts.created_at DESC
        """
    ).fetchall()


def users_data(db):
    return db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()


def competitions_data(db):
    return db.execute("SELECT * FROM competitions ORDER BY id DESC").fetchall()


@web.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "message": t("health_ok")})


@web.route("/")
def home():
    active_auth = request.args.get("auth", "login")
    if active_auth not in {"login", "register", "reset"}:
        active_auth = "login"
    competitions = get_db().execute(
        "SELECT * FROM competitions WHERE status = 'published' ORDER BY start_at LIMIT 4"
    ).fetchall()
    return render_template("home.html", competitions=competitions, active_auth=active_auth)


@web.route("/competitions")
def competitions():
    competitions = get_db().execute(
        "SELECT * FROM competitions WHERE status = 'published' ORDER BY start_at"
    ).fetchall()
    return render_template("competitions.html", competitions=competitions)


@web.route("/competitions/<slug>")
def competition_detail(slug):
    competition = get_db().execute(
        "SELECT * FROM competitions WHERE slug = ? AND status = 'published'",
        (slug,),
    ).fetchone()
    if not competition:
        abort(404)
    return render_template("competition_detail.html", competition=competition)


@web.route("/teams", methods=["GET", "POST"])
def teams():
    db = get_db()
    user = current_user()
    if request.method == "POST":
        guard = require_login()
        if guard:
            return guard
        db.execute(
            """
            INSERT INTO teams (name, target_event, need_text, description, contact, captain_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                request.form["name"],
                request.form["target_event"],
                request.form["need_text"],
                request.form["description"],
                request.form["contact"],
                user["id"],
                datetime.utcnow().isoformat(),
            ),
        )
        db.commit()
        add_audit("create_team", "team", request.form["name"], "pending review")
        flash(
            "Team submitted for review."
            if session.get("lang") == "en"
            else "队伍已提交，等待审核。"
        )
        return redirect(url_for("web.teams"))

    teams_rows = db.execute(
        """
        SELECT teams.*, users.real_name AS captain_name
        FROM teams JOIN users ON users.id = teams.captain_id
        WHERE teams.status = 'approved'
        ORDER BY teams.created_at DESC
        """
    ).fetchall()
    my_team = None
    pending_requests = []
    if user:
        my_team = db.execute(
            "SELECT * FROM teams WHERE captain_id = ? ORDER BY created_at DESC LIMIT 1",
            (user["id"],),
        ).fetchone()
        if my_team:
            pending_requests = db.execute(
                """
                SELECT team_join_requests.id, team_join_requests.created_at, users.real_name, users.username
                FROM team_join_requests
                JOIN users ON users.id = team_join_requests.user_id
                WHERE team_join_requests.team_id = ? AND team_join_requests.status = 'pending'
                ORDER BY team_join_requests.created_at DESC
                """,
                (my_team["id"],),
            ).fetchall()
    return render_template("teams.html", teams=teams_rows, my_team=my_team, pending_requests=pending_requests)


@web.route("/teams/<int:team_id>/join", methods=["POST"])
def join_team(team_id):
    guard = require_login()
    if guard:
        return guard
    user = current_user()
    get_db().execute(
        """
        INSERT OR IGNORE INTO team_join_requests (team_id, user_id, status, created_at)
        VALUES (?, ?, 'pending', ?)
        """,
        (team_id, user["id"], datetime.utcnow().isoformat()),
    )
    get_db().commit()
    add_audit("join_request", "team", team_id)
    flash("Join request sent." if session.get("lang") == "en" else "加入申请已提交。")
    return redirect(url_for("web.teams"))


@web.route("/teams/requests/<int:request_id>/<action>", methods=["POST"])
def handle_team_request(request_id, action):
    guard = require_login()
    if guard:
        return guard
    user = current_user()
    db = get_db()
    row = db.execute(
        """
        SELECT team_join_requests.*, teams.captain_id
        FROM team_join_requests
        JOIN teams ON teams.id = team_join_requests.team_id
        WHERE team_join_requests.id = ?
        """,
        (request_id,),
    ).fetchone()
    if not row or row["captain_id"] != user["id"]:
        abort(403)
    if action == "approve":
        db.execute("UPDATE team_join_requests SET status = 'approved' WHERE id = ?", (request_id,))
        db.execute(
            """
            INSERT OR IGNORE INTO team_members (team_id, user_id, role, joined_at)
            VALUES (?, ?, 'member', ?)
            """,
            (row["team_id"], row["user_id"], datetime.utcnow().isoformat()),
        )
    else:
        db.execute("UPDATE team_join_requests SET status = 'rejected' WHERE id = ?", (request_id,))
    db.commit()
    add_audit(f"team_request_{action}", "team_request", request_id)
    return redirect(url_for("web.teams"))


@web.route("/forum", methods=["GET", "POST"])
def forum():
    db = get_db()
    user = current_user()
    if request.method == "POST":
        guard = require_login()
        if guard:
            return guard
        if user["muted"]:
            flash("Your account is muted." if session.get("lang") == "en" else "你的账号已被禁言。")
            return redirect(url_for("web.forum"))
        db.execute(
            "INSERT INTO forum_posts (user_id, title, content, status, created_at) VALUES (?, ?, ?, 'visible', ?)",
            (user["id"], request.form["title"], request.form["content"], datetime.utcnow().isoformat()),
        )
        db.commit()
        add_audit("publish_post", "forum_post", request.form["title"])
        return redirect(url_for("web.forum"))

    posts = db.execute(
        """
        SELECT forum_posts.*, users.real_name, users.username
        FROM forum_posts JOIN users ON users.id = forum_posts.user_id
        WHERE forum_posts.status = 'visible'
        ORDER BY forum_posts.created_at DESC
        """
    ).fetchall()
    my_posts = []
    if user:
        my_posts = db.execute(
            "SELECT * FROM forum_posts WHERE user_id = ? ORDER BY created_at DESC",
            (user["id"],),
        ).fetchall()
    return render_template("forum.html", posts=posts, my_posts=my_posts)


@web.route("/forum/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    guard = require_login()
    if guard:
        return guard
    user = current_user()
    db = get_db()
    post = db.execute("SELECT * FROM forum_posts WHERE id = ?", (post_id,)).fetchone()
    if not post or (post["user_id"] != user["id"] and user["role"] != "admin"):
        abort(403)
    db.execute("DELETE FROM forum_posts WHERE id = ?", (post_id,))
    db.commit()
    add_audit("delete_post", "forum_post", post_id)
    return redirect(url_for("web.forum"))


@web.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        guard = require_login()
        if guard:
            return guard
        user = current_user()
        get_db().execute(
            "INSERT INTO feedback_entries (user_id, content, status, created_at) VALUES (?, ?, 'new', ?)",
            (user["id"], request.form["content"], datetime.utcnow().isoformat()),
        )
        get_db().commit()
        add_audit("submit_feedback", "feedback", "new")
        flash("Feedback submitted." if session.get("lang") == "en" else "反馈已提交。")
        return redirect(url_for("web.feedback"))
    return render_template("feedback.html")


@web.route("/profile", methods=["GET", "POST"])
def profile():
    guard = require_login()
    if guard:
        return render_template("profile.html", locked=True, user=None, memberships=[])
    user = current_user()
    if request.method == "POST":
        get_db().execute(
            "UPDATE users SET bio = ?, skills = ?, intention = ? WHERE id = ?",
            (request.form["bio"], request.form["skills"], request.form["intention"], user["id"]),
        )
        get_db().commit()
        add_audit("update_profile", "user", user["id"])
        return redirect(url_for("web.profile"))
    memberships = get_db().execute(
        """
        SELECT teams.name, teams.target_event, team_members.role
        FROM team_members JOIN teams ON teams.id = team_members.team_id
        WHERE team_members.user_id = ?
        ORDER BY teams.created_at DESC
        """,
        (user["id"],),
    ).fetchall()
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
    return render_template("profile.html", locked=False, user=user, memberships=memberships)


@web.route("/auth/register", methods=["POST"])
def register():
    form = request.form
    db = get_db()
    if form.get("captcha", "").strip() != "11":
        flash("Human verification failed." if session.get("lang") == "en" else "人机验证失败。")
        return auth_home_redirect("register")
    if form.get("password") != form.get("confirm_password"):
        flash("Passwords do not match." if session.get("lang") == "en" else "两次密码不一致。")
        return auth_home_redirect("register")
    existing = db.execute(
        "SELECT id FROM users WHERE username = ? OR student_id = ?",
        (form.get("username"), form.get("student_id")),
    ).fetchone()
    if existing:
        flash("User already exists." if session.get("lang") == "en" else "用户已存在。")
        return auth_home_redirect("register")
    now = datetime.utcnow().isoformat()
    db.execute(
        """
        INSERT INTO users
        (real_name, student_id, phone, username, password_hash, role, status, muted, bio, skills, intention, created_at, last_login_at)
        VALUES (?, ?, ?, ?, ?, 'student', 'active', 0, '', '', '', ?, ?)
        """,
        (
            form.get("real_name"),
            form.get("student_id"),
            internal_phone_value(form.get("student_id")),
            form.get("username"),
            generate_password_hash(form.get("password")),
            now,
            now,
        ),
    )
    db.commit()
    user = db.execute("SELECT * FROM users WHERE username = ?", (form.get("username"),)).fetchone()
    session["user_id"] = user["id"]
    add_audit("register", "user", user["id"])
    return redirect(url_for("web.home"))


@web.route("/auth/login", methods=["POST"])
def login():
    form = request.form
    user = get_db().execute("SELECT * FROM users WHERE username = ?", (form.get("username"),)).fetchone()
    if not user or not check_password_hash(user["password_hash"], form.get("password", "")):
        flash("Login failed." if session.get("lang") == "en" else "登录失败。")
        return auth_home_redirect("login")
    if user["status"] == "banned":
        flash("Account banned." if session.get("lang") == "en" else "账号已被封禁。")
        return auth_home_redirect("login")
    session["user_id"] = user["id"]
    get_db().execute("UPDATE users SET last_login_at = ? WHERE id = ?", (datetime.utcnow().isoformat(), user["id"]))
    get_db().commit()
    add_audit("login", "user", user["id"])
    return redirect(url_for("web.home"))


@web.route("/auth/reset-password", methods=["POST"])
def reset_password():
    form = request.form
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? AND student_id = ?",
        (form.get("username"), form.get("student_id")),
    ).fetchone()
    if not user:
        flash("Identity check failed." if session.get("lang") == "en" else "身份校验失败。")
        return auth_home_redirect("reset")
    if not form.get("new_password"):
        flash("Please enter a new password." if session.get("lang") == "en" else "请输入新密码。")
        return auth_home_redirect("reset")
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (generate_password_hash(form.get("new_password")), user["id"]),
    )
    db.commit()
    add_audit("reset_password", "user", user["id"])
    flash("Password reset completed." if session.get("lang") == "en" else "密码已重置。")
    return auth_home_redirect("login")


@web.route("/auth/logout", methods=["POST"])
def logout():
    user = current_user()
    if user:
        add_audit("logout", "user", user["id"])
    session.clear()
    target = request.form.get("next") or request.args.get("next")
    return internal_redirect(target, "web.home")


@web.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    user = current_user()
    if is_admin(user):
        return redirect(url_for("web.admin"))

    next_target = request.values.get("next") or url_for("web.admin")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        candidate = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not candidate or not check_password_hash(candidate["password_hash"], password) or not is_admin(candidate):
            flash("Administrator login failed." if session.get("lang") == "en" else "管理员登录失败。")
            return render_template("admin_login.html", next_target=next_target)
        if candidate["status"] == "banned":
            flash("Account banned." if session.get("lang") == "en" else "账号已被封禁。")
            return render_template("admin_login.html", next_target=next_target)
        session["user_id"] = candidate["id"]
        get_db().execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), candidate["id"]),
        )
        get_db().commit()
        add_audit("admin_login", "user", candidate["id"])
        return internal_redirect(next_target, "web.admin")

    return render_template("admin_login.html", next_target=next_target)


@web.route("/admin")
def admin():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    return render_template(
        "admin.html",
        stats=admin_stats(db),
        active_admin="overview",
    )


@web.route("/admin/site")
def admin_site():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    return render_template(
        "admin_site.html",
        stats=admin_stats(db),
        competitions=competitions_data(db),
        active_admin="site",
    )


@web.route("/admin/review")
def admin_review():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    return render_template(
        "admin_review.html",
        stats=admin_stats(db),
        pending_teams=pending_teams_data(db),
        active_admin="review",
    )


@web.route("/admin/feedback")
def admin_feedback():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    return render_template(
        "admin_feedback.html",
        stats=admin_stats(db),
        feedback_items=feedback_items_data(db),
        active_admin="feedback",
    )


@web.route("/admin/forum")
def admin_forum():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    return render_template(
        "admin_forum.html",
        stats=admin_stats(db),
        posts=forum_posts_data(db),
        active_admin="forum",
    )


@web.route("/admin/users")
def admin_users():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    return render_template(
        "admin_users.html",
        stats=admin_stats(db),
        users=users_data(db),
        active_admin="users",
    )


@web.route("/admin/settings", methods=["POST"])
def admin_update_settings():
    guard = require_admin()
    if guard:
        return guard
    set_site_setting("site_name", request.form.get("site_name", "").strip() or "温州肯恩大学AI社团竞赛平台")
    set_site_setting("hero_eyebrow", request.form.get("hero_eyebrow", "").strip() or "WKU CS Innovation Platform")
    set_site_setting("hero_title", request.form.get("hero_title", "").strip() or "把比赛、组队、论坛和个人成长放进一个真正可上线的平台。")
    set_site_setting(
        "hero_subtitle",
        request.form.get("hero_subtitle", "").strip()
        or "这个版本采用模块化单体架构、服务端渲染、SQLite 持久化和会话认证，适合先做 MVP 再稳定上线。",
    )
    add_audit("admin_update_settings", "site_settings", "global")
    flash("Settings updated." if session.get("lang") == "en" else "站点内容已更新。")
    return admin_redirect("web.admin")


@web.route("/admin/competitions/create", methods=["POST"])
def admin_create_competition():
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    title = request.form.get("title", "").strip()
    slug = request.form.get("slug", "").strip() or slugify_text(title)
    if not title or not slug:
        flash("Title and slug are required." if session.get("lang") == "en" else "赛事名称和标识不能为空。")
        return admin_redirect("web.admin")
    existing = db.execute("SELECT id FROM competitions WHERE slug = ?", (slug,)).fetchone()
    if existing:
        flash("Slug already exists." if session.get("lang") == "en" else "赛事标识已存在。")
        return admin_redirect("web.admin")
    db.execute(
        """
        INSERT INTO competitions
        (slug, title, category, summary, start_at, end_at, location, official_url, reference_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            slug,
            title,
            request.form.get("category", "").strip(),
            request.form.get("summary", "").strip(),
            request.form.get("start_at", "").strip(),
            request.form.get("end_at", "").strip(),
            request.form.get("location", "").strip(),
            request.form.get("official_url", "").strip(),
            request.form.get("reference_url", "").strip(),
            request.form.get("status", "draft").strip() or "draft",
        ),
    )
    db.commit()
    add_audit("admin_create_competition", "competition", slug)
    flash("Competition created." if session.get("lang") == "en" else "赛事已创建。")
    return admin_redirect("web.admin")


@web.route("/admin/competitions/<int:competition_id>/update", methods=["POST"])
def admin_update_competition(competition_id):
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    title = request.form.get("title", "").strip()
    slug = request.form.get("slug", "").strip() or slugify_text(title)
    if not title or not slug:
        flash("Title and slug are required." if session.get("lang") == "en" else "赛事名称和标识不能为空。")
        return admin_redirect("web.admin")
    existing = db.execute("SELECT id FROM competitions WHERE slug = ? AND id != ?", (slug, competition_id)).fetchone()
    if existing:
        flash("Slug already exists." if session.get("lang") == "en" else "赛事标识已存在。")
        return admin_redirect("web.admin")
    db.execute(
        """
        UPDATE competitions
        SET slug = ?, title = ?, category = ?, summary = ?, start_at = ?, end_at = ?, location = ?,
            official_url = ?, reference_url = ?, status = ?
        WHERE id = ?
        """,
        (
            slug,
            title,
            request.form.get("category", "").strip(),
            request.form.get("summary", "").strip(),
            request.form.get("start_at", "").strip(),
            request.form.get("end_at", "").strip(),
            request.form.get("location", "").strip(),
            request.form.get("official_url", "").strip(),
            request.form.get("reference_url", "").strip(),
            request.form.get("status", "draft").strip() or "draft",
            competition_id,
        ),
    )
    db.commit()
    add_audit("admin_update_competition", "competition", competition_id)
    flash("Competition updated." if session.get("lang") == "en" else "赛事已更新。")
    return admin_redirect("web.admin")


@web.route("/admin/competitions/<int:competition_id>/delete", methods=["POST"])
def admin_delete_competition(competition_id):
    guard = require_admin()
    if guard:
        return guard
    get_db().execute("DELETE FROM competitions WHERE id = ?", (competition_id,))
    get_db().commit()
    add_audit("admin_delete_competition", "competition", competition_id)
    flash("Competition deleted." if session.get("lang") == "en" else "赛事已删除。")
    return admin_redirect("web.admin")


@web.route("/admin/teams/<int:team_id>/<action>", methods=["POST"])
def admin_team_action(team_id, action):
    guard = require_admin()
    if guard:
        return guard
    get_db().execute("UPDATE teams SET status = ? WHERE id = ?", ("approved" if action == "approve" else "rejected", team_id))
    get_db().commit()
    add_audit(f"admin_team_{action}", "team", team_id)
    return admin_redirect("web.admin_review")


@web.route("/admin/feedback/<int:feedback_id>/<action>", methods=["POST"])
def admin_feedback_action(feedback_id, action):
    guard = require_admin()
    if guard:
        return guard
    status = "resolved" if action == "resolve" else "new"
    get_db().execute("UPDATE feedback_entries SET status = ? WHERE id = ?", (status, feedback_id))
    get_db().commit()
    add_audit(f"admin_feedback_{action}", "feedback", feedback_id)
    return admin_redirect("web.admin_feedback")


@web.route("/admin/posts/<int:post_id>/<action>", methods=["POST"])
def admin_post_action(post_id, action):
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    if action == "hide":
        db.execute("UPDATE forum_posts SET status = 'hidden' WHERE id = ?", (post_id,))
    elif action == "show":
        db.execute("UPDATE forum_posts SET status = 'visible' WHERE id = ?", (post_id,))
    elif action == "delete":
        db.execute("DELETE FROM forum_posts WHERE id = ?", (post_id,))
    db.commit()
    add_audit(f"admin_post_{action}", "forum_post", post_id)
    return admin_redirect("web.admin_forum")


@web.route("/admin/users/<int:user_id>/<action>", methods=["POST"])
def admin_user_action(user_id, action):
    guard = require_admin()
    if guard:
        return guard
    db = get_db()
    if action == "ban":
        db.execute("UPDATE users SET status = 'banned' WHERE id = ?", (user_id,))
    elif action == "unban":
        db.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))
    elif action == "mute":
        db.execute("UPDATE users SET muted = 1 WHERE id = ?", (user_id,))
    elif action == "unmute":
        db.execute("UPDATE users SET muted = 0 WHERE id = ?", (user_id,))
    db.commit()
    add_audit(f"admin_user_{action}", "user", user_id)
    return admin_redirect("web.admin_users")

