# 🚀 部署指南（大学生友好版）

## 你会得到什么

```
用户浏览器
    │  只发送 { provider, model, text }
    ▼
Cloudflare Worker（你的免费代理）
    │  用服务端保存的 Key 调用 AI
    ▼
各家 AI API（Claude / DeepSeek / 通义 / GLM / Kimi）
```

**用户永远看不到你的 API Key。**

---

## 第一步：注册 Cloudflare（免费）

1. 打开 https://cloudflare.com → 右上角「Sign Up」
2. 填邮箱 + 密码完成注册，不需要绑卡

---

## 第二步：安装工具

打开电脑终端（Windows 用「命令提示符」或「PowerShell」，Mac 用「终端」）：

```bash
# 安装 Node.js（如果还没有）：https://nodejs.org 下载 LTS 版本

# 安装 Wrangler（Cloudflare 的命令行工具）
npm install -g wrangler

# 登录 Cloudflare
npx wrangler login
# 会自动打开浏览器，点「Allow」授权即可
```

---

## 第三步：创建项目文件夹

```bash
mkdir notes-proxy
cd notes-proxy

# 把 worker.js 和 wrangler.toml 两个文件放到这个文件夹里
```

---

## 第四步：创建限流用的 KV 数据库

```bash
npx wrangler kv namespace create RATE_LIMIT_KV
```

输出类似：
```
✅ Created namespace "RATE_LIMIT_KV"
Add the following to your wrangler.toml:
[[kv_namespaces]]
binding = "RATE_LIMIT_KV"
id = "abc123def456..."   ← 复制这串 ID
```

打开 `wrangler.toml`，把 `你的KV_namespace_id_填这里` 替换为刚才复制的 ID。

---

## 第五步：设置 API Key（存在服务端，用户不可见）

```bash
# 逐条运行，每次输入对应的 Key 后回车
npx wrangler secret put CLAUDE_API_KEY
npx wrangler secret put DEEPSEEK_API_KEY
npx wrangler secret put QWEN_API_KEY
npx wrangler secret put GLM_API_KEY
npx wrangler secret put KIMI_API_KEY
```

> 💡 没有哪家的 Key 可以先跳过，Worker 里会返回"未配置"的友好提示。

---

## 第六步：部署 Worker

```bash
npx wrangler deploy
```

输出类似：
```
✅ Deployed notes-ai-proxy
   https://notes-ai-proxy.你的名字.workers.dev
```

复制这个地址。

---

## 第七步：修改前端配置

打开 `physics_notes_app.jsx`，找到第 9 行：

```js
const PROXY_URL = "https://notes-ai-proxy.YOUR_SUBDOMAIN.workers.dev/api/convert";
```

改成你实际的 Worker 地址：

```js
const PROXY_URL = "https://notes-ai-proxy.你的名字.workers.dev/api/convert";
```

---

## 第八步：部署前端

把修改好的 `physics_notes_app.jsx` 部署到任意静态托管服务（都免费）：

| 平台 | 方法 |
|------|------|
| **Cloudflare Pages**（推荐） | 上传文件夹，自动构建 |
| **Vercel** | `npx vercel` 一键部署 |
| **GitHub Pages** | push 到 repo 自动发布 |

---

## 完成！测试一下

打开你的前端页面 → 选个 AI → 粘贴笔记 → 点「AI 转换」

如果报错，运行以下命令查看 Worker 日志：
```bash
npx wrangler tail
```

---

## 限流说明

默认配置：**每个 IP 每小时最多 20 次请求**

如需修改，打开 `worker.js` 找到：
```js
const RATE_LIMIT = {
  maxRequests: 20,   // ← 改这里
  windowSecs: 3600,  // ← 3600秒 = 1小时
};
```
改完后重新 `npx wrangler deploy` 即可生效。

---

## 免费额度

| 资源 | 免费额度 |
|------|---------|
| Worker 请求次数 | 每天 **10 万次** |
| KV 读操作 | 每天 **10 万次** |
| KV 写操作 | 每天 **1000 次** |

对于个人或小团队完全够用。超出后按量计费，非常便宜。
