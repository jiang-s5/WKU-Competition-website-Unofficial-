from datetime import datetime

from werkzeug.security import generate_password_hash

from .db import get_db


def seed_initial_data():
    db = get_db()

    settings = [
        ("site_name", "温州肯恩大学AI社团竞赛平台"),
        ("hero_eyebrow", "WKU CS Innovation Platform"),
        ("hero_title", "把比赛、组队、论坛和个人成长放进一个真正可上线的平台。"),
        ("hero_subtitle", "这个版本采用模块化单体架构、服务端渲染、SQLite 持久化和会话认证，适合先做 MVP 再稳定上线。"),
    ]
    for item in settings:
        db.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES (?, ?)", item)

    competitions = [
        (
            "aigc-innovation",
            "中国高校计算机大赛AIGC创新赛",
            "AIGC",
            "聚焦 AIGC 创新应用与实践展示，具体规则、日程与报名要求请以官网公布为准。",
            "以官网公布为准",
            "以官网公布为准",
            "参赛形式与地点以官网公布为准",
            "https://aigc.vivo.com.cn/#/home",
            "https://aigc.vivo.com.cn/#/home",
            "published",
        ),
        (
            "digital-skills-computing",
            "全国大学生数字技能应用大赛计算机技能应用赛",
            "计算机技能应用",
            "面向计算机技能应用方向，具体赛项说明、报名方式与时间安排请以官网公布为准。",
            "以官网公布为准",
            "以官网公布为准",
            "参赛形式与地点以官网公布为准",
            "https://www.cnccac.com/",
            "https://www.cnccac.com/",
            "published",
        ),
        (
            "digital-ai-application",
            "全国大学生数字应用大赛人工智能应用赛",
            "人工智能应用",
            "聚焦人工智能应用实践方向，具体赛道设置、报名流程与时间请以官网公布为准。",
            "以官网公布为准",
            "以官网公布为准",
            "参赛形式与地点以官网公布为准",
            "https://www.cnccac.com/rgzn",
            "https://www.cnccac.com/rgzn",
            "published",
        ),
        (
            "ai-innovation-entrepreneurship",
            "全国大学生人工智能+创新创业大赛",
            "人工智能+创新创业",
            "面向人工智能与创新创业结合方向，赛程、规则和报名要求请以官网公布为准。",
            "以官网公布为准",
            "以官网公布为准",
            "参赛形式与地点以官网公布为准",
            "http://rgzn.52jingsai.com",
            "http://rgzn.52jingsai.com",
            "published",
        ),
    ]
    db.execute("DELETE FROM competitions")
    for item in competitions:
        db.execute(
            """
            INSERT INTO competitions
            (slug, title, category, summary, start_at, end_at, location, official_url, reference_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            item,
        )

    admin = db.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if admin is None:
        now = datetime.utcnow().isoformat()
        db.execute(
            """
            INSERT INTO users
            (real_name, student_id, phone, username, password_hash, role, status, muted, bio, skills, intention, created_at, last_login_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Platform Admin",
                "ADMIN0001",
                "13800000000",
                "admin",
                generate_password_hash("Admin@123456"),
                "admin",
                "active",
                0,
                "Default administrator account",
                "platform governance",
                "site operation",
                now,
                now,
            ),
        )

    db.commit()

