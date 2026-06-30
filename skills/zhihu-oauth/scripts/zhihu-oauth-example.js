/**
 * 知乎 OAuth 2.0 接入示例 (Node.js / Express)
 *
 * 环境变量：
 *   ZHIHU_APP_ID
 *   ZHIHU_APP_KEY
 *   ZHIHU_REDIRECT_URI
 */

const express = require('express');
const axios = require('axios');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const ZHIHU_APP_ID = process.env.ZHIHU_APP_ID;
const ZHIHU_APP_KEY = process.env.ZHIHU_APP_KEY;
const ZHIHU_REDIRECT_URI = process.env.ZHIHU_REDIRECT_URI;

// 生产环境请使用 Redis 等持久化存储
const stateStore = new Map();

// 1. 生成授权 URL
app.get('/api/auth/zhihu/url', (req, res) => {
  const redirect_uri = req.query.redirect_uri || ZHIHU_REDIRECT_URI;
  const state = crypto.randomUUID();
  stateStore.set(state, { redirect_uri, timestamp: Date.now() });

  const authorizeUrl = `https://openapi.zhihu.com/authorize?` +
    `redirect_uri=${encodeURIComponent(redirect_uri)}` +
    `&app_id=${ZHIHU_APP_ID}` +
    `&response_type=code` +
    `&state=${state}`;

  res.json({ authorize_url: authorizeUrl, state });
});

// 2. 处理授权回调
app.post('/api/auth/zhihu/callback', async (req, res) => {
  const { code, state, redirect_uri } = req.body;

  if (!stateStore.has(state)) {
    return res.status(400).json({ error: 'Invalid state' });
  }
  const stored = stateStore.get(state);
  stateStore.delete(state);

  try {
    // 换取 access_token
    const tokenResponse = await axios.post('https://openapi.zhihu.com/access_token', {
      app_id: ZHIHU_APP_ID,
      app_key: ZHIHU_APP_KEY,
      grant_type: 'authorization_code',
      redirect_uri: redirect_uri || stored.redirect_uri,
      code,
    });

    const { access_token, expires_in } = tokenResponse.data;

    // 获取用户信息
    const userResponse = await axios.get('https://openapi.zhihu.com/user', {
      headers: { Authorization: `Bearer ${access_token}` },
    });

    res.json({
      access_token,
      expires_in,
      user: userResponse.data,
    });
  } catch (error) {
    const message = error.response?.data || error.message;
    res.status(500).json({ error: message });
  }
});

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
