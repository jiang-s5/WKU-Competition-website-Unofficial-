(function () {
  function read(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function write(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getSiteLang() {
    return localStorage.getItem("site-lang") || "zh";
  }

  function localized(messages) {
    const lang = getSiteLang();
    return messages[lang] || messages.zh;
  }

  const CLEAN_RELEASE_VERSION = "2026-04-14-no-sms-release";

  function resetReleaseStorage() {
    const currentVersion = localStorage.getItem("wku-release-version");
    if (currentVersion === CLEAN_RELEASE_VERSION) {
      return;
    }
    [
      "wku-users",
      "wku-platform-user",
      "wku-platform-username",
      "wku-team-requests",
      "wku-teams"
    ].forEach((key) => localStorage.removeItem(key));
    localStorage.setItem("wku-release-version", CLEAN_RELEASE_VERSION);
  }

  resetReleaseStorage();

  function getUsers() {
    return read("wku-users", []);
  }

  function saveUsers(users) {
    write("wku-users", users);
  }

  function getCurrentUserName() {
    return localStorage.getItem("wku-platform-user") || "";
  }

  function getCurrentUsername() {
    return localStorage.getItem("wku-platform-username") || "";
  }

  function getCurrentUser() {
    const username = getCurrentUsername();
    if (username) {
      return getUsers().find((user) => user.username === username) || null;
    }
    const name = getCurrentUserName();
    return getUsers().find((user) => user.name === name) || null;
  }

  function getUserByIdentity(identity) {
    if (!identity) {
      return null;
    }
    return getUsers().find((user) => user.username === identity || user.name === identity) || null;
  }

  function saveCurrentUser(name) {
    const trimmed = (name || "").trim() || "计算机学院同学";
    const users = getUsers();
    const current = getCurrentUser();
    const existing = current
      ? users.find((user) => user.username === current.username)
      : users.find((user) => user.name === trimmed);
    if (existing) {
      existing.name = trimmed;
      existing.lastLogin = new Date().toISOString();
      setCurrentUser(existing);
    } else {
      const newUser = {
        name: trimmed,
        username: trimmed,
        studentId: "",
        password: "",
        avatar: "",
        bio: "",
        skills: "",
        status: "normal",
        muted: false,
        role: "student",
        registerTime: new Date().toISOString(),
        lastLogin: new Date().toISOString()
      };
      users.push(newUser);
      setCurrentUser(newUser);
    }
    saveUsers(users);
    return trimmed;
  }

  function setCurrentUser(user) {
    localStorage.setItem("wku-platform-user", user.name);
    localStorage.setItem("wku-platform-username", user.username || user.name);
  }

  function logoutCurrentUser() {
    localStorage.removeItem("wku-platform-user");
    localStorage.removeItem("wku-platform-username");
  }

  function updateCurrentUserProfile(payload) {
    const users = getUsers();
    const current = getCurrentUser();
    if (!current) {
      return { ok: false };
    }
    const target = users.find((user) => user.username === current.username);
    if (!target) {
      return { ok: false };
    }

    if (typeof payload.name === "string") {
      target.name = payload.name.trim() || target.name;
    }
    if (typeof payload.bio === "string") {
      target.bio = payload.bio.trim();
    }
    if (typeof payload.skills === "string") {
      target.skills = payload.skills.trim();
    }
    if (typeof payload.avatar === "string") {
      target.avatar = payload.avatar;
    }

    target.updatedAt = new Date().toISOString();
    saveUsers(users);
    setCurrentUser(target);
    return { ok: true, user: target };
  }

  function registerAuthUser(payload) {
    const users = getUsers();
    if (!payload.name || !payload.studentId || !payload.username || !payload.password) {
      return { ok: false, message: localized({
        zh: "请完整填写姓名、学号、用户名和密码。",
        en: "Please complete real name, student ID, username, and password.",
        ja: "氏名、学籍番号、ユーザー名、パスワードをすべて入力してください。"
      }) };
    }
    if (payload.password !== payload.confirmPassword) {
      return { ok: false, message: localized({
        zh: "两次输入的密码不一致。",
        en: "The two password entries do not match.",
        ja: "2回入力したパスワードが一致しません。"
      }) };
    }
    if (users.some((user) => user.username === payload.username)) {
      return { ok: false, message: localized({
        zh: "该用户名已被注册。",
        en: "This username has already been registered.",
        ja: "このユーザー名はすでに登録されています。"
      }) };
    }
    if (users.some((user) => user.studentId === payload.studentId)) {
      return { ok: false, message: localized({
        zh: "该学号已存在。",
        en: "This student ID already exists.",
        ja: "この学籍番号はすでに存在します。"
      }) };
    }
    const user = {
      name: payload.name,
      username: payload.username,
      studentId: payload.studentId,
      password: payload.password,
      avatar: "",
      bio: "",
      skills: "",
      status: "normal",
      muted: false,
      role: "student",
      registerTime: new Date().toISOString(),
      lastLogin: new Date().toISOString()
    };
    users.push(user);
    saveUsers(users);
    setCurrentUser(user);
    return { ok: true, user };
  }

  function loginAuthUser(username, password) {
    const user = getUsers().find((item) => item.username === username);
    if (!user) {
      return { ok: false, message: localized({
        zh: "用户名不存在。",
        en: "Username does not exist.",
        ja: "ユーザー名が存在しません。"
      }) };
    }
    if (user.password !== password) {
      return { ok: false, message: localized({
        zh: "密码错误。",
        en: "Incorrect password.",
        ja: "パスワードが正しくありません。"
      }) };
    }
    if (user.status === "banned") {
      return { ok: false, message: localized({
        zh: "当前账号已被封禁，无法登录。",
        en: "This account has been banned and cannot log in.",
        ja: "このアカウントは停止されているためログインできません。"
      }) };
    }
    user.lastLogin = new Date().toISOString();
    saveUsers(getUsers().map((item) => item.username === user.username ? user : item));
    setCurrentUser(user);
    return { ok: true, user };
  }

  function resetPasswordByIdentity(payload) {
    const users = getUsers();
    const user = users.find((item) =>
      item.username === payload.username &&
      item.studentId === payload.studentId
    );
    if (!user) {
      return { ok: false, message: localized({
        zh: "用户名和学号未匹配成功。",
        en: "Username and student ID do not match.",
        ja: "ユーザー名と学籍番号が一致しません。"
      }) };
    }
    if (!payload.newPassword) {
      return { ok: false, message: localized({
        zh: "请输入新密码。",
        en: "Please enter a new password.",
        ja: "新しいパスワードを入力してください。"
      }) };
    }
    user.password = payload.newPassword;
    saveUsers(users);
    return { ok: true, message: localized({
      zh: "密码已重置，请使用新密码登录。",
      en: "Password has been reset. Please log in with the new password.",
      ja: "パスワードが再設定されました。新しいパスワードでログインしてください。"
    }) };
  }

  function isBanned() {
    const user = getCurrentUser();
    return !!(user && user.status === "banned");
  }

  function isMuted() {
    const user = getCurrentUser();
    return !!(user && user.muted);
  }

  function addTeamRequest(payload) {
    const requests = read("wku-team-requests", []);
    requests.unshift({
      id: Date.now(),
      applicant: getCurrentUserName(),
      status: "pending",
      createdAt: new Date().toISOString(),
      ...payload
    });
    write("wku-team-requests", requests);
  }

  function getTeamRequests() {
    return read("wku-team-requests", []);
  }

  function inferTeamEventSlug(targetEvent) {
    const eventMap = {
      "中国高校计算机大赛AIGC创新赛": "aigc-innovation",
      "全国大学生数字技能应用大赛计算机技能应用赛": "digital-skills-computing",
      "全国大学生数字应用大赛人工智能应用赛": "digital-ai-application",
      "全国大学生人工智能+创新创业大赛": "ai-innovation-entrepreneurship"
    };
    return eventMap[targetEvent] || "";
  }

  function getTeams() {
    const defaults = [];
    const stored = read("wku-teams", defaults);
    const approvedRequests = getTeamRequests().filter((item) => item.status === "approved");
    let changed = false;
    stored.forEach((team) => {
      if (!team.eventSlug) {
        team.eventSlug = inferTeamEventSlug(team.targetEvent);
        changed = true;
      }
      if (!team.location) {
        team.location = "地点待沟通";
        changed = true;
      }
      if (!Array.isArray(team.members)) {
        team.members = [];
        changed = true;
      }
      if (!Array.isArray(team.joinRequests)) {
        team.joinRequests = [];
        changed = true;
      }
    });
    for (const item of approvedRequests) {
      const exists = stored.find((team) => team.name === item.teamName);
      if (!exists) {
        stored.push({
          id: "team-" + item.id,
          name: item.teamName,
          eventSlug: item.eventSlug || inferTeamEventSlug(item.targetEvent),
          targetEvent: item.targetEvent,
          location: item.teamLocation || "地点待沟通",
          need: item.teamNeed,
          desc: item.teamDesc,
          captain: item.applicant || "未命名队长",
          contact: item.contact || item.applicant || "待补充",
          members: [item.applicant || "未命名队长"],
          joinRequests: []
        });
        changed = true;
      }
    }
    if (changed) {
      write("wku-teams", stored);
    }
    return stored;
  }

  function saveTeams(teams) {
    write("wku-teams", teams);
  }

  function requestJoinTeam(teamName) {
    const applicant = getCurrentUserName();
    const teams = getTeams();
    const team = teams.find((item) => item.name === teamName);
    if (!team || !applicant) return { ok: false, reason: "missing" };
    if (team.members.includes(applicant)) return { ok: false, reason: "member" };
    if ((team.joinRequests || []).some((item) => item.user === applicant && item.status === "pending")) {
      return { ok: false, reason: "pending" };
    }
    team.joinRequests = team.joinRequests || [];
    team.joinRequests.push({
      id: Date.now(),
      user: applicant,
      status: "pending",
      createdAt: new Date().toISOString()
    });
    saveTeams(teams);
    return { ok: true };
  }

  function approveJoinRequest(teamName, requestId) {
    const teams = getTeams();
    const team = teams.find((item) => item.name === teamName);
    if (!team) return;
    const request = (team.joinRequests || []).find((item) => item.id === requestId);
    if (!request) return;
    request.status = "approved";
    if (!team.members.includes(request.user)) {
      team.members.push(request.user);
    }
    team.joinRequests = team.joinRequests.filter((item) => item.id !== requestId);
    saveTeams(teams);
  }

  function rejectJoinRequest(teamName, requestId) {
    const teams = getTeams();
    const team = teams.find((item) => item.name === teamName);
    if (!team) return;
    team.joinRequests = (team.joinRequests || []).filter((item) => item.id !== requestId);
    saveTeams(teams);
  }

  function removeTeamMember(teamName, memberName) {
    const teams = getTeams();
    const team = teams.find((item) => item.name === teamName);
    if (!team) return;
    team.members = (team.members || []).filter((item) => item !== memberName || item === team.captain);
    saveTeams(teams);
  }

  function addFeedback(payload) {
    const feedbacks = read("wku-feedback-list", []);
    feedbacks.unshift({
      id: Date.now(),
      user: getCurrentUserName(),
      createdAt: new Date().toISOString(),
      status: "new",
      ...payload
    });
    write("wku-feedback-list", feedbacks);
  }

  function getFeedbacks() {
    return read("wku-feedback-list", []);
  }

  function dedupeList(values) {
    return [...new Set((values || []).filter(Boolean))];
  }

  function normalizeForumComment(comment, index) {
    return {
      id: comment.id || Date.now() + index,
      author: comment.author || "匿名用户",
      authorUsername: comment.authorUsername || "",
      content: comment.content || "",
      createdAt: comment.createdAt || new Date().toISOString()
    };
  }

  function normalizeForumPost(post) {
    const normalized = {
      ...post,
      author: post.author || "匿名用户",
      authorUsername: post.authorUsername || "",
      status: post.status || "visible",
      views: Number.isFinite(Number(post.views)) ? Number(post.views) : 0,
      likeUsers: dedupeList(post.likeUsers),
      favoriteUsers: dedupeList(post.favoriteUsers),
      dislikeUsers: dedupeList(post.dislikeUsers),
      commentsList: Array.isArray(post.commentsList) ? post.commentsList.map(normalizeForumComment) : []
    };
    if (!normalized.author && normalized.authorUsername) {
      const matched = getUserByIdentity(normalized.authorUsername);
      normalized.author = matched ? matched.name : normalized.authorUsername;
    }
    return normalized;
  }

  function saveForumPosts(posts) {
    write("wku-forum-posts", posts.map(normalizeForumPost));
  }

  function addForumPost(payload) {
    const posts = getForumPosts();
    const currentUser = getCurrentUser();
    posts.unshift({
      id: Date.now(),
      author: getCurrentUserName(),
      authorUsername: currentUser ? currentUser.username : "",
      createdAt: new Date().toISOString(),
      status: "visible",
      views: 0,
      likeUsers: [],
      favoriteUsers: [],
      dislikeUsers: [],
      commentsList: [],
      ...payload
    });
    saveForumPosts(posts);
  }

  function getForumPosts() {
    return read("wku-forum-posts", [
      {
        id: 1,
        author: "创新实践社",
        authorUsername: "innovation-lab",
        createdAt: "2026-04-08T12:00:00.000Z",
        title: "有没有同学想组队冲 AIGC 创新赛？",
        content: "欢迎对 AIGC 应用、作品展示、提示工程方向感兴趣的同学来讨论。",
        status: "visible",
        views: 245,
        likeUsers: ["alice", "bob", "carol"],
        favoriteUsers: ["alice", "david"],
        dislikeUsers: [],
        commentsList: [
          {
            id: 101,
            author: "王同学",
            authorUsername: "wang",
            content: "我偏提示工程和应用展示方向，可以一起交流一下。",
            createdAt: "2026-04-08T13:15:00.000Z"
          },
          {
            id: 102,
            author: "李同学",
            authorUsername: "li",
            content: "如果后面要做作品演示和答辩材料，我也想一起准备。",
            createdAt: "2026-04-08T15:42:00.000Z"
          }
        ]
      },
      {
        id: 2,
        author: "建模训练营",
        authorUsername: "modeling-camp",
        createdAt: "2026-04-07T09:30:00.000Z",
        title: "人工智能应用赛备赛资料分享",
        content: "这里整理了人工智能应用赛的资料入口、选题方向和项目展示思路。",
        status: "visible",
        views: 188,
        likeUsers: ["eve", "frank"],
        favoriteUsers: ["frank"],
        dislikeUsers: ["grace"],
        commentsList: [
          {
            id: 201,
            author: "周同学",
            authorUsername: "zhou",
            content: "如果后续有项目展示模板，也欢迎继续补充。",
            createdAt: "2026-04-07T10:10:00.000Z"
          }
        ]
      }
    ]).map(normalizeForumPost);
  }

  function getUserForumPosts(username) {
    const user = getUserByIdentity(username);
    return getForumPosts().filter((post) => {
      if (user) {
        return post.authorUsername === user.username || post.author === user.name;
      }
      return post.author === username || post.authorUsername === username;
    });
  }

  function getForumCounts(post) {
    const normalized = normalizeForumPost(post);
    return {
      views: normalized.views,
      likes: normalized.likeUsers.length,
      favorites: normalized.favoriteUsers.length,
      dislikes: normalized.dislikeUsers.length,
      comments: normalized.commentsList.length
    };
  }

  function toggleForumReaction(postId, reactionType) {
    const currentUser = getCurrentUser();
    if (!currentUser) {
      return { ok: false, reason: "login" };
    }
    if (currentUser.status === "banned") {
      return { ok: false, reason: "banned" };
    }

    const posts = getForumPosts();
    const target = posts.find((post) => post.id === postId);
    if (!target) {
      return { ok: false, reason: "missing" };
    }

    const actor = currentUser.username || currentUser.name;
    const keyMap = {
      like: "likeUsers",
      favorite: "favoriteUsers",
      dislike: "dislikeUsers"
    };
    const targetKey = keyMap[reactionType];
    if (!targetKey) {
      return { ok: false, reason: "invalid" };
    }

    target[targetKey] = target[targetKey] || [];
    const exists = target[targetKey].includes(actor);
    if (exists) {
      target[targetKey] = target[targetKey].filter((item) => item !== actor);
    } else {
      target[targetKey].push(actor);
      if (reactionType === "like") {
        target.dislikeUsers = (target.dislikeUsers || []).filter((item) => item !== actor);
      }
      if (reactionType === "dislike") {
        target.likeUsers = (target.likeUsers || []).filter((item) => item !== actor);
      }
    }

    saveForumPosts(posts);
    const updated = posts.find((post) => post.id === postId);
    return {
      ok: true,
      active: !exists,
      counts: getForumCounts(updated)
    };
  }

  function addForumComment(postId, content) {
    const currentUser = getCurrentUser();
    if (!currentUser) {
      return { ok: false, reason: "login" };
    }
    if (currentUser.status === "banned") {
      return { ok: false, reason: "banned" };
    }
    if (currentUser.muted) {
      return { ok: false, reason: "muted" };
    }

    const trimmed = (content || "").trim();
    if (!trimmed) {
      return { ok: false, reason: "empty" };
    }

    const posts = getForumPosts();
    const target = posts.find((post) => post.id === postId);
    if (!target) {
      return { ok: false, reason: "missing" };
    }

    target.commentsList = target.commentsList || [];
    target.commentsList.unshift({
      id: Date.now(),
      author: currentUser.name,
      authorUsername: currentUser.username || currentUser.name,
      content: trimmed,
      createdAt: new Date().toISOString()
    });

    saveForumPosts(posts);
    const updated = posts.find((post) => post.id === postId);
    return {
      ok: true,
      counts: getForumCounts(updated),
      commentsList: updated.commentsList
    };
  }

  function updateForumPost(postId, payload) {
    const posts = getForumPosts();
    const current = getCurrentUser();
    const target = posts.find((post) => post.id === postId);
    const canEdit = !!(target && current && (target.author === current.name || target.authorUsername === current.username));
    if (!canEdit) {
      return { ok: false, message: "no_permission" };
    }
    target.title = payload.title;
    target.content = payload.content;
    target.updatedAt = new Date().toISOString();
    saveForumPosts(posts);
    return { ok: true };
  }

  function deleteForumPost(postId) {
    const posts = getForumPosts();
    const current = getCurrentUser();
    const target = posts.find((post) => post.id === postId);
    const canDelete = !!(target && current && (target.author === current.name || target.authorUsername === current.username));
    if (!canDelete) {
      return { ok: false, message: "no_permission" };
    }
    saveForumPosts(posts.filter((post) => post.id !== postId));
    return { ok: true };
  }

  function setForumPostStatus(postId, status) {
    const posts = getForumPosts();
    const target = posts.find((post) => post.id === postId);
    if (!target) {
      return { ok: false };
    }
    target.status = status;
    saveForumPosts(posts);
    return { ok: true };
  }

  function getHeroVideoConfig() {
    return read("wku-hero-video-config", {
      src: "hero-video.mp4",
      title: "温州肯恩大学AI社团竞赛平台",
      subtitle: "向下滚动，镜头会随着页面推进逐步展开。"
    });
  }

  function saveHeroVideoConfig(config) {
    const current = getHeroVideoConfig();
    write("wku-hero-video-config", {
      ...current,
      ...config
    });
  }

  window.PlatformData = {
    getUsers,
    saveUsers,
    getCurrentUserName,
    getCurrentUsername,
    getCurrentUser,
    getUserByIdentity,
    saveCurrentUser,
    setCurrentUser,
    logoutCurrentUser,
    updateCurrentUserProfile,
    registerAuthUser,
    loginAuthUser,
    resetPasswordByIdentity,
    isBanned,
    isMuted,
    addTeamRequest,
    getTeamRequests,
    getTeams,
    saveTeams,
    requestJoinTeam,
    approveJoinRequest,
    rejectJoinRequest,
    removeTeamMember,
    addFeedback,
    getFeedbacks,
    addForumPost,
    getForumPosts,
    getUserForumPosts,
    getForumCounts,
    toggleForumReaction,
    addForumComment,
    updateForumPost,
    deleteForumPost,
    saveForumPosts,
    setForumPostStatus,
    getHeroVideoConfig,
    saveHeroVideoConfig
  };
})();

