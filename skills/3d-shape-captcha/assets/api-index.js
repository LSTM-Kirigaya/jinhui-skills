import r from "@/api/request"
import long_r from "@/api/long_request"

// 首页
export const reqGetServerInfo = () => r({
    url: "/home/get-server-info", method: "GET"
});

export const reqGetNews = () => r({
    url: "/home/get-news", method: "GET"
});

export const reqGetMoreBlogs = (pageId) => r({
    url: "/home/get-more-blogs", method: "GET",
    params: { pageId }
});

export const reqGetTops = () => r({
    url: "/home/get-tops", method: "GET"
});

// 登录 & 注册 & 登出

export const reqSignUp = (name, password, imgUrl, email = '', code = '') => r({
    url: "/user/sign-up", method: "POST",
    data: { name, password, imgUrl, email, code }
});

export const reqCheckName = (name) => r({
    url: "/user/check-name", method: "GET",
    params: { name }
});

export const reqCheckEmail = (email) => r({
    url: "/user/check-email", method: "GET",
    params: { email }
});

export const reqSendVerificationCode = (email, captchaToken = '') => r({
    url: "/ses/send-verification-code", method: "POST",
    data: { email, captchaToken }
});

export const reqGenerateCaptcha = () => r({
    url: "/captcha/generate", method: "GET"
});

export const reqVerifyCaptcha = (captchaId, shapeIndex) => r({
    url: "/captcha/verify", method: "POST",
    data: { captchaId, shapeIndex }
});

export const reqVerifyRegisterCode = (email, code) => r({
    url: "/ses/verify-register-code", method: "POST",
    data: { email, code }
});

export const reqSignIn = (name, password) => r({
    url: "/user/sign-in", method: "POST",
    data: { name, password }
});

export const reqLogout = () => r({
    url: "/user/logout", method: "GET"
});

export const reqModifyUserInfo = (imgUrl, email, bio, egoId) => r({
    url: "/user/modify-user-info", method: "POST",
    data: { imgUrl, email, bio, egoId }
});

export const reqUpdateEmail = (email) => r({
    url: "/user/update-email", method: "POST",
    data: { email }
});

export const reqGetPublicUserInfo = (id) => r({
    url: `/user/public-info/${id}`, method: "GET"
});


// 个人信息
export const reqGetFavBangumi = () => r({
    url: "/me/bilibili-bangumi", method : "GET"
});

export const reqGetColumnInfo = () => r({
    url: "/me/zhihu-column", method : "GET"
});

export const reqGetProject = () => r({
    url: "/me/project", method: "GET"
});

export const reqGetLearnProgress = () => r({
    url: "/me/learn-progress", method: "GET"
});

export const reqGetTodo = () => r({
    url: "/me/todo-list", method: "GET"
});

export const reqGetDevLog = () => r({
    url: "/me/dev-log", method: "GET"
});

export const reqGetOpenSource = () => r({
    url: "/me/open-source", method: "GET"
});

export const reqGetForHaru = () => r({
    url: "/me/for-haru", method: "GET"
})

// KTools
export const reqSR = (image, id) => r({
    url: "/cv/sr", method: "POST",
    data: { image, id }
});

export const reqSRQuery = (id, type) => r({
    url: "/cv/srQuery", method: "GET",
    params : { id, type }
});

// KMarkdown
export const reqGetKdPrintComponent = () => r({
    url: "/kd/get-print-component", method: "GET"
});

// kg
export const reqGetKGQuery = (text, limit) => long_r({
    url: "/kg/kg-node-query", method: "GET",
    params: { text, limit }
});

export const reqGetKGQueryRelation = (start, end, limit) => long_r({
    url: "/kg/kg-relation-query", method: "GET",
    params: { start, end , limit }
});

// blog
export const reqInitBlog = (maxBlogOnePage) => r({
    url: "/blog/init-blog", method: "GET",
    params: { maxBlogOnePage }
});

export const reqQueryRangeBlog = (min_seq, max_seq) => r({
    url: "/blog/range-query-blog", method: "GET",
    params: { min_seq, max_seq }
});

export const reqQueryBlogByPageId = (pageId) => r({
    url: "/blog/range-query-blog-by-pageId", method: "GET",
    params: { pageId }
});

export const reqFetchArticle = (blogName) => r({
    url: "/blog/fetch-blog", method: "GET",
    params: { blogName }
});


export const reqFetchArticleBySeq = (seq) => r({
    url: "/blog/fetch-blog-by-seq", method: "GET",
    params: { seq }
});


export const reqSimpleRecommand = (blogName, RecNum) => r({
    url: "/blog/simple-recommand-by-name", method: "GET",
    params : { blogName, RecNum }
});

// 按话题搜索
export const reqInitTopicSearch = (maxBlogOnePage, topicName) => r({
    url: "/blog/search-by-tags", method: "GET",
    params : { maxBlogOnePage, topicName }
});

export const reqQueryRangeBlogByTopic = (topicName, begin, end) => r({
    url: "/blog/range-query-blog-by-topic", method: "GET",
    params : { topicName, begin, end }
});

export const reqGetAllTopics = () => r({
    url: "/blog/get-all-topics", method: "POST"
})

// 按输入名字搜索
export const reqSearchBlogsByName = (names) => r({
    url: "/blog/search-by-names", method: "GET",
    params: { names }
});

export const reqGetHotTopics = () => r({
    url: "/blog/get-hot-topics", method: "GET"
});

export const reqCreateBlog = (password, name, tags, adjustTime, imgUrl, isPrivate, text) => r({
    url: "/blog/create-blog", method: "POST",
    data: { password, name, tags, adjustTime, imgUrl, isPrivate, text }
});

export const reqDeleteBlog = (password, seq) => r({
    url: "/blog/delete-blog-by-seq", method: "GET",
    params: { password, seq }
});

export const reqModifyBlog = (password, seq, name, tags, adjustTime, imgUrl, isPrivate, text) => r({
    url: "/blog/modify-blog-by-seq", method: "POST",
    data: { password, seq, name, tags, adjustTime, imgUrl, isPrivate, text }
});

// 博客评论区
export const reqPublishBlogComment = (blogSeq, publisherId, atId, text, createTime) => r({
    url: "/blog/publish-comment", method: "POST",
    data: { blogSeq, publisherId, atId, text, createTime }
});

export const reqDeleteBlogComment = (commentId) => r({
    url: "/blog/delete-comment", method: "POST",
    data: { commentId }
});

export const reqModifyBlogComment = (commentId, text) => r({
    url: "/blog/modify-comment", method: "GET",
    params: { commentId, text }
});

export const reqGetCommentsByBlogSeq = (blogSeq) => r({
    url: "/blog/get-comment-by-blog-seq", method: "GET",
    params: { blogSeq }
});

export const reqGetAdministraterName = () => r({
    url: "/blog/get-aministrater-name", method: "GET"
});


// PPT
export const reqInitPpt = (maxPptOnePage) => r({
    url: "/slidev/init-ppt", method: "GET",
    params: { maxPptOnePage }
});

// music
export const reqQueryStaffsByPageId = (pageId) => r({
    url: "/music/query-staffs-by-pageId", method: "GET",
    params: { pageId }
});

export const reqInitStaffs = () => r({
    url: "/music/init-staff", method: "GET"
});

export const reqPublishStaff = (publisherId, createTime, alphaTex, imgUrl, config) => r({
    url: "/music/publish-staff", method: "POST",
    data: { publisherId, createTime, alphaTex, imgUrl, config }
});

export const reqDeleteStaff = (staffId) => r({
    url: "/music/delete-staff", method: "POST",
    data : { staffId }
});

export const reqModfyStaff = (staffId, alphaTex, imgUrl, config) => r({
    url: "/music/modify-staff", method: "POST",
    data: { staffId, alphaTex, imgUrl, config }
});

export const reqGetStaffById = (staffId) => r({
    url: "/music/get-staff-by-id", method: "GET",
    params: { staffId }
});


export const reqQueryRangePpt = (min_seq, max_seq) => r({
    url: "/slidev/range-query-ppt", method: "GET",
    params: { min_seq, max_seq }
});

// 私人 LLM

export const reqResumeChatgptConversion = () => r({
    url: "/llm/resume-chatgpt-conversion", method: "GET"
});

export const reqGetChatgptAnswer = ( question, clear ) => long_r({
    url: "/llm/get-chatgpt-answer", method: "POST",
    data : { question, clear }
});


// 密码
export const reqCheckBlogPassword = (password, operation) => r({
    url: "/password/check-blog-password", method: "GET",
    params: { password, operation }
});



// 获取随机图片
export const reqGetRandomBangumiImgUrl = () => r({
    url: "/thirdparty/random-image-url", method: "GET"
});

// 获取天气信息
export const reqGetWeather = () => long_r({
    url: "/thirdparty/get-city-weather-by-ip", method: "GET"
});

// 获取最新评论
export const reqGetNewestComments = (start, end) => r({
    url: "/comment/newest-comments",
    method: "POST",
    data: { start, end }
});

// 获取网页元数据
export const reqGetWebMeta = (url) => r({
    url: "/webmeta/get",
    method: "POST",
    data: { url }
});

// OAuth
export const reqOAuthApprove = (clientId, redirectUri, scope, state) => r({
    url: "/oauth/approve",
    method: "POST",
    data: { clientId, redirectUri, scope, state }
});

export const reqOAuthDeny = (redirectUri, state) => r({
    url: "/oauth/deny",
    method: "POST",
    data: { redirectUri, state }
});

// GitHub OAuth
export const reqGitHubLogin = () => r({
    url: "/oauth/github/login",
    method: "GET"
});

export const reqGitHubBind = () => r({
    url: "/oauth/github/bind",
    method: "GET"
});

export const reqGitHubRegister = (data) => r({
    url: "/oauth/github/register",
    method: "POST",
    data
});

export const reqGitHubStatus = () => r({
    url: "/oauth/github/status",
    method: "GET"
});

export const reqGitHubUnbind = () => r({
    url: "/oauth/github/unbind",
    method: "POST"
});

// Watcha OAuth
export const reqWatchaLogin = () => r({
    url: "/oauth/watcha/login",
    method: "GET"
});

export const reqWatchaBind = () => r({
    url: "/oauth/watcha/bind",
    method: "GET"
});

export const reqWatchaRegister = (data) => r({
    url: "/oauth/watcha/register",
    method: "POST",
    data
});

export const reqWatchaStatus = () => r({
    url: "/oauth/watcha/status",
    method: "GET"
});

export const reqWatchaUnbind = () => r({
    url: "/oauth/watcha/unbind",
    method: "POST"
});

// Access Token 管理
export const reqCreateAccessToken = (name, expiresDays) => r({
    url: "/user/access-token/create",
    method: "POST",
    data: { name, expiresDays }
});

export const reqListAccessTokens = () => r({
    url: "/user/access-tokens",
    method: "GET"
});

export const reqDeleteAccessToken = (id) => r({
    url: "/user/access-token/delete",
    method: "POST",
    data: { id }
});

// 友情链接
export const reqListFriendLinks = () => r({
    url: "/friendlink/list",
    method: "GET"
});

export const reqCreateFriendLink = (data) => r({
    url: "/friendlink/create",
    method: "POST",
    data
});

export const reqUpdateFriendLink = (data) => r({
    url: "/friendlink/update",
    method: "POST",
    data
});

export const reqDeleteFriendLink = (data) => r({
    url: "/friendlink/delete",
    method: "POST",
    data
});