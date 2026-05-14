(function () {
  const translations = {
    common: {
      brand: {
        zh: "温州肯恩大学AI社团竞赛平台",
        en: "WKU AI Club Competition Platform",
        ja: "WKU 計算機学院 イノベーション大会プラットフォーム"
      },
      nav_home: { zh: "首页", en: "Home", ja: "ホーム" },
      nav_browse: { zh: "浏览赛事", en: "Events", ja: "大会一覧" },
      nav_detail: { zh: "赛事详情", en: "Details", ja: "大会詳細" },
      nav_teams: { zh: "寻找团队", en: "Teams", ja: "チーム募集" },
      nav_profile: { zh: "个人主页", en: "Profile", ja: "プロフィール" },
      nav_feedback: { zh: "意见反馈", en: "Feedback", ja: "フィードバック" },
      nav_forum: { zh: "论坛", en: "Forum", ja: "フォーラム" },
      guest: { zh: "访客模式", en: "Guest", ja: "ゲスト" },
      signed_in: { zh: "已登录", en: "Signed In", ja: "ログイン済み" },
      signed_out: { zh: "未登录", en: "Not Signed In", ja: "未ログイン" },
      logout: { zh: "退出登录", en: "Logout", ja: "ログアウト" }
    },
    index: {
      hero_kicker: { zh: "WKU CS Innovation Platform", en: "WKU CS Innovation Platform", ja: "WKU CS Innovation Platform" },
      hero_title: {
        zh: "找比赛、组团队、做认证，把科创路径放在一个入口里。",
        en: "Find competitions, build teams, and put your innovation journey into one clean entry point.",
        ja: "大会を探し、チームを組み、科創の道をひとつの入口に集約します。"
      },
      hero_subtitle: {
        zh: "视频会在整个页面中持续流畅播放，平台内容与视觉风格保持统一。",
        en: "The video now plays smoothly across the whole page while the platform keeps a unified visual language.",
        ja: "動画はページ全体で滑らかに再生され、全体のデザインも統一されています。"
      },
      quick_title: { zh: "快速进入", en: "Quick Access", ja: "クイックアクセス" },
      quick_desc: { zh: "保留最常用的几个入口，让信息更集中，整体风格与首屏保持一致。", en: "Keep the most-used entries focused and visually aligned with the hero section.", ja: "よく使う入口だけを残し、ヒーローと統一感のある見た目にしています。" },
      auth_entry: { zh: "个人访问入口", en: "Personal Access", ja: "個人アクセス" },
      auth_title: { zh: "登录 / 注册", en: "Login / Register", ja: "ログイン / 登録" },
      auth_desc: { zh: "使用个人账号进入平台，保存你的个人主页、团队状态与赛事浏览记录。", en: "Use your account to save your profile, team status, and browsing records.", ja: "個人アカウントでログインし、プロフィールやチーム状態、閲覧記録を保存できます。" },
      login_tab: { zh: "登录", en: "Login", ja: "ログイン" },
      register_tab: { zh: "注册", en: "Register", ja: "登録" },
      reset_tab: { zh: "找回密码", en: "Reset Password", ja: "パスワード再設定" },
      username_ph: { zh: "用户名", en: "Username", ja: "ユーザー名" },
      password_ph: { zh: "密码", en: "Password", ja: "パスワード" },
      human_check: { zh: "我不是机器人，确认本人登录", en: "I am not a robot and confirm this login request.", ja: "私はロボットではなく、本人によるログインです。" },
      login_hint: { zh: "登录使用用户名 + 密码。若密码遗忘，可切换到“找回密码”。", en: "Login uses username + password. If you forgot your password, switch to reset.", ja: "ログインはユーザー名とパスワードで行います。忘れた場合は再設定へ切り替えてください。" },
      real_name_ph: { zh: "真实姓名", en: "Real Name", ja: "氏名" },
      student_id_ph: { zh: "学生号", en: "Student ID", ja: "学生番号" },
      phone_ph: { zh: "电话号码", en: "Phone Number", ja: "電話番号" },
      confirm_password_ph: { zh: "确认密码", en: "Confirm Password", ja: "パスワード確認" },
      sms_ph: { zh: "短信验证码", en: "SMS Verification Code", ja: "SMS認証コード" },
      send_sms: { zh: "发送验证码", en: "Send Code", ja: "コード送信" },
      captcha_ph: { zh: "请输入 8 + 3 的结果", en: "Enter the result of 8 + 3", ja: "8 + 3 の答えを入力してください" },
      captcha_label: { zh: "人机验证", en: "Human Check", ja: "人間確認" },
      reset_password_ph: { zh: "新密码", en: "New Password", ja: "新しいパスワード" },
      platform_note_title: { zh: "平台说明", en: "Platform Notes", ja: "プラットフォーム説明" },
      platform_note_heading: { zh: "简洁，但功能完整", en: "Minimal, but complete", ja: "シンプル、でも十分" },
      platform_note_body: { zh: "你可以浏览热门赛事、进入详情页查看通知和官网链接、寻找招募中的团队，或编辑个人主页展示你的科创经历与特长。", en: "Browse events, open detailed notices and official links, find recruiting teams, or edit your profile to present your experience.", ja: "大会閲覧、詳細通知と公式リンク確認、募集チーム検索、プロフィール編集ができます。" }
    },
    forum: {
      title: { zh: "学生论坛", en: "Student Forum", ja: "学生フォーラム" },
      desc: { zh: "同学们可以在这里交流备赛资料、组队想法、参赛经验和赛事问题。", en: "Students can share resources, team ideas, competition experience, and questions here.", ja: "ここでは資料共有、チーム募集、参加経験や質問の交流ができます。" }
    },
    profile: {
      title: { zh: "个人主页", en: "Profile", ja: "プロフィール" }
    },
    teams: {
      title: { zh: "寻找团队", en: "Find a Team", ja: "チームを探す" }
    },
    feedback: {
      title: { zh: "意见反馈", en: "Feedback", ja: "フィードバック" }
    },
    browse: {
      title: { zh: "浏览赛事列表", en: "Browse Events", ja: "大会一覧" }
    },
    detail: {
      title: { zh: "赛事详情页", en: "Event Detail", ja: "大会詳細" }
    }
  };

  function getLang() {
    return localStorage.getItem("site-lang") || "zh";
  }

  function setLang(lang) {
    localStorage.setItem("site-lang", lang);
  }

  function textFor(key, lang, page) {
    const source = (page && translations[page] && translations[page][key]) || translations.common[key];
    return source ? (source[lang] || source.zh) : null;
  }

  function applyCommon(lang) {
    const brand = document.querySelector(".brand div:last-child");
    if (brand) brand.textContent = textFor("brand", lang);
    const mappings = [
      ['a[href="index.html"]', "nav_home"],
      ['a[href="browse.html"]', "nav_browse"],
      ['a[href="detail.html"]', "nav_detail"],
      ['a[href="teams.html"]', "nav_teams"],
      ['a[href="profile.html"]', "nav_profile"],
      ['a[href="feedback.html"]', "nav_feedback"],
      ['a[href="forum.html"]', "nav_forum"]
    ];
    mappings.forEach(([selector, key]) => {
      const el = document.querySelector(`.nav ${selector}`);
      if (el) el.textContent = textFor(key, lang);
    });
    const chip = document.getElementById("userChip");
    if (chip && chip.textContent.trim() === "访客模式") {
      chip.textContent = textFor("guest", lang);
    }
  }

  function applyPage(lang, page) {
    const pageMap = {
      index: [
        [".cinema-kicker", "hero_kicker"],
        ["#heroVideoTitle", "hero_title"],
        ["#heroVideoSubtitle", "hero_subtitle"],
        [".section-head h2", "quick_title"],
        [".section-head .muted", "quick_desc"],
        ["#authEntry", "auth_entry"],
        ["#authTitle", "auth_title"],
        ["#authDesc", "auth_desc"],
        ["#loginSwitch", "login_tab"],
        ["#registerSwitch", "register_tab"],
        ["#resetSwitch", "reset_tab"],
        ["#loginUsername", "username_ph", "placeholder"],
        ["#loginPassword", "password_ph", "placeholder"],
        ["#loginHumanLabel", "human_check"],
        ["#loginSubmit", "login_tab"],
        ["#loginHint", "login_hint"],
        ["#registerRealName", "real_name_ph", "placeholder"],
        ["#registerStudentId", "student_id_ph", "placeholder"],
        ["#registerPhone", "phone_ph", "placeholder"],
        ["#registerUsername", "username_ph", "placeholder"],
        ["#registerPassword", "password_ph", "placeholder"],
        ["#registerPasswordConfirm", "confirm_password_ph", "placeholder"],
        ["#registerSmsCode", "sms_ph", "placeholder"],
        ["#registerSmsButton", "send_sms"],
        ["#registerCaptcha", "captcha_ph", "placeholder"],
        ["#captchaLabel", "captcha_label"],
        ["#registerSubmit", "register_tab"],
        ["#resetUsername", "username_ph", "placeholder"],
        ["#resetStudentId", "student_id_ph", "placeholder"],
        ["#resetPhone", "phone_ph", "placeholder"],
        ["#resetSmsCode", "sms_ph", "placeholder"],
        ["#resetSmsButton", "send_sms"],
        ["#resetPassword", "reset_password_ph", "placeholder"],
        ["#resetSubmit", "reset_tab"],
        ["#platformNoteTitle", "platform_note_title"],
        ["#platformNoteHeading", "platform_note_heading"],
        ["#platformNoteBody", "platform_note_body"]
      ],
      forum: [[".section-head h2", "title"], [".section-head .muted", "desc"]],
      profile: [[".section-head h2", "title"]],
      teams: [[".section-head h2", "title"]],
      feedback: [[".section-head h2", "title"]],
      browse: [[".section-head h2", "title"]],
      detail: [[".section-head h2", "title"]]
    };
    (pageMap[page] || []).forEach(([selector, key, attr]) => {
      const el = document.querySelector(selector);
      const value = textFor(key, lang, page);
      if (el && value) {
        if (attr === "placeholder") {
          el.placeholder = value;
        } else {
          el.textContent = value;
        }
      }
    });
  }

  function renderSwitcher(page) {
    const target = document.getElementById("langSwitcher");
    if (!target) return;
    const lang = getLang();
    target.className = "lang-switcher";
    target.innerHTML = ["zh", "en", "ja"].map((item) =>
      `<button type="button" data-lang="${item}" class="${item === lang ? "active" : ""}">${item.toUpperCase()}</button>`
    ).join("");
    target.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => {
        setLang(button.dataset.lang);
        apply(button.dataset.lang, page);
      });
    });
  }

  function apply(lang, page) {
    applyCommon(lang);
    applyPage(lang, page);
    renderSwitcher(page);
    document.dispatchEvent(new CustomEvent("site-lang-change", { detail: { lang, page } }));
  }

  window.FrontendI18n = {
    t(page, key) {
      return textFor(key, getLang(), page);
    },
    init(page) {
      apply(getLang(), page);
    }
  };
})();

