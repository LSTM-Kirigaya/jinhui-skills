#!/usr/bin/env node
/**
 * 观猹 OAuth2.0 接入示例 (Node.js)
 */

const crypto = require('crypto');
const querystring = require('querystring');

// ========== 配置 ==========
const CLIENT_ID = 'your_client_id';
const CLIENT_SECRET = 'your_client_secret'; // 公开客户端可不填
const REDIRECT_URI = 'https://myapp.com/callback';
const SCOPE = 'read email';
// ==========================

/**
 * 生成 PKCE 参数
 */
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto
    .createHash('sha256')
    .update(verifier)
    .digest('base64url');
  return { verifier, challenge };
}

/**
 * 构建授权 URL
 */
function buildAuthorizeUrl(codeChallenge) {
  const params = {
    response_type: 'code',
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    scope: SCOPE,
    state: 'random_string',
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
  };
  return `https://watcha.cn/oauth/authorize?${querystring.stringify(params)}`;
}

/**
 * 使用授权码换取 Token
 */
async function exchangeCode(code, codeVerifier) {
  const body = {
    grant_type: 'authorization_code',
    code,
    redirect_uri: REDIRECT_URI,
    client_id: CLIENT_ID,
  };
  if (CLIENT_SECRET) body.client_secret = CLIENT_SECRET;
  if (codeVerifier) body.code_verifier = codeVerifier;

  const resp = await fetch('https://watcha.cn/oauth/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: querystring.stringify(body),
  });
  return resp.json();
}

/**
 * 刷新 AccessToken
 */
async function refreshToken(refreshToken) {
  const body = {
    grant_type: 'refresh_token',
    refresh_token: refreshToken,
  };
  const resp = await fetch('https://watcha.cn/oauth/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: querystring.stringify(body),
  });
  return resp.json();
}

/**
 * 获取用户信息
 */
async function getUserInfo(accessToken) {
  const resp = await fetch(
    `https://watcha.cn/oauth/api/userinfo?access_token=${encodeURIComponent(accessToken)}`
  );
  return resp.json();
}

/**
 * 校验 Token
 */
async function introspect(token, tokenTypeHint = 'access_token') {
  const resp = await fetch('https://watcha.cn/oauth/api/introspect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: querystring.stringify({
      token,
      token_type_hint: tokenTypeHint,
    }),
  });
  return resp.json();
}

module.exports = {
  generatePKCE,
  buildAuthorizeUrl,
  exchangeCode,
  refreshToken,
  getUserInfo,
  introspect,
};

// 示例用法
if (require.main === module) {
  const { verifier, challenge } = generatePKCE();
  console.log('PKCE verifier:', verifier);
  console.log('PKCE challenge:', challenge);
  console.log('Authorize URL:', buildAuthorizeUrl(challenge));
}
