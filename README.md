# 📐 笔记 → PDF · AI 智能排版

> 将含有 LaTeX 公式的理工科笔记，一键转换为排版精美的 HTML 笔记，支持打印为 PDF。
> 同时提供 **PDF 教材总结**功能，上传教材后 AI 自动提取知识点、公式与大纲。

**在线体验：** [notes-pdf.pages.dev]

---

## ✨ 功能特性

### 📝 笔记转换
- 输入含 LaTeX 公式的笔记原文，AI 自动识别结构并排版
- 转换前可自定义格式：详细程度、重点标注框、例题展示、公式样式
- KaTeX 实时渲染数学公式，支持全部 LaTeX 命令
- 一键打印 / 保存为 PDF（浏览器原生打印）
- 内置大学物理、高等数学、物理化学三套示例模板

### 📚 PDF 总结
- 拖拽或点击上传 PDF 教材（自动提取前 80 页文字）
- 可选总结类型：知识点提炼 / 重点公式 / 章节大纲 / 考点梳理（支持多选）
- 可选详细程度：详细 / 中等 / 简洁
- 总结结果可直接复制，或一键转入笔记排版流程

### 🔒 安全设计
- 所有 AI API Key 存储在服务端（Cloudflare Worker 环境变量），用户完全不可见
- 前端基于 DOMPurify 对 AI 返回内容进行 XSS 过滤
- 内置 IP 滑动窗口限流，防止 API 额度被滥用

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | React 18 + Vite |
| 数学渲染 | KaTeX 0.16 |
| XSS 防护 | DOMPurify |
| PDF 解析 | PDF.js |
| AI 模型 | Groq（Llama 3.3 70B） |
| 前端部署 | Cloudflare Pages |
| 后端代理 | Cloudflare Workers |
| 限流存储 | Cloudflare KV |

---

## 📁 项目结构

```
├── notes-pdf/              # 前端项目
│   ├── src/
│   │   ├── App.jsx         # 主应用（全部逻辑）
│   │   └── main.jsx        # React 入口
│   ├── public/
│   │   └── _redirects      # Cloudflare Pages SPA 路由
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── worker.js               # Cloudflare Worker 后端代理
├── wrangler.toml           # Worker 部署配置
└── README.md
```

---

## 🚀 本地开发

### 环境要求
- Node.js 18+
- npm 9+

### 启动前端

```bash
cd notes-pdf
npm install
npm run dev
# 默认在 http://localhost:5173 打开
```

### 启动 Worker（本地模拟）

```bash
# 安装 Wrangler
npm install -g wrangler

# 在 worker.js 同目录下创建 .dev.vars 文件，填入 Key：
# GROQ_API_KEY=gsk_xxx

# 启动本地 Worker
npx wrangler dev
# 默认在 http://localhost:8787
```

然后将 `notes-pdf/src/App.jsx` 第 8 行改为本地地址：
```js
const PROXY_URL = "http://localhost:8787/api/convert";
```

---

## ☁️ 部署指南

### 第一步：部署 Cloudflare Worker（后端）

**1. 注册 Cloudflare 账号**（免费）：[cloudflare.com](https://cloudflare.com)

**2. 安装 Wrangler 并登录**
```bash
npm install -g wrangler
npx wrangler login
```

**3. （可选）创建 KV 命名空间用于限流**
```bash
npx wrangler kv namespace create RATE_LIMIT_KV
# 将输出的 id 填入 wrangler.toml，并取消相关行的注释
```

**4. 设置 API Key**
```bash
npx wrangler secret put GROQ_API_KEY
# 输入你的 Groq API Key（gsk_...）后回车
```

**5. 部署**
```bash
npx wrangler deploy
# 部署成功后会输出 Worker 地址，例如：
# https://notes-ai-proxy.你的名字.workers.dev
```

---

### 第二步：部署前端到 Cloudflare Pages

**1. 修改 PROXY_URL**

打开 `notes-pdf/src/App.jsx` 第 8 行，填入你的 Worker 地址：
```js
const PROXY_URL = "https://notes-ai-proxy.你的名字.workers.dev/api/convert";
```

**2. 打包**
```bash
cd notes-pdf
npm install
npm run build
# 生成 dist/ 文件夹
```

**3. 上传到 Cloudflare Pages**

- 打开 [Cloudflare 控制台](https://dash.cloudflare.com) → Workers & Pages → Create → Pages → Upload assets
- 项目名填 `notes-pdf`，将 `dist/` 文件夹拖入上传
- 点击 Deploy site

部署完成后会获得 `xxx.pages.dev` 的免费域名。

---

## 🔑 获取免费 API Key

本项目默认使用 **Groq**（完全免费，速度极快）：

1. 打开 [console.groq.com](https://console.groq.com) 注册账号
2. 左侧菜单 → API Keys → Create API Key
3. 复制 `gsk_` 开头的 Key

> Groq 每天提供免费调用额度，Llama 3.3 70B 处理笔记排版完全够用。

---

## ⚙️ 限流配置

在 `worker.js` 顶部修改：

```js
const RATE_LIMIT = {
  maxRequests: 20,   // 每个 IP 每小时最多请求次数
  windowSecs: 3600,  // 时间窗口（秒）
};
```

> 需要先启用 KV 命名空间（见部署第三步），限流才会生效。未配置 KV 时自动跳过限流。

---

## 📖 使用说明

### 笔记转换

1. 在左侧输入框粘贴笔记内容，公式使用 LaTeX 语法书写：
   ```
   速度公式：\vec{v} = \frac{d\vec{r}}{dt}
   ```
2. 点击顶部学科标签切换示例模板（切换时预览自动清空）
3. 点击「✨ AI 转换」，在弹窗中设置排版格式后确认
4. 右侧实时渲染排版结果，点击「🖨 打印 / 保存 PDF」导出

### PDF 总结

1. 切换到「📚 PDF 总结」标签
2. 拖拽或点击上传 PDF 文件（教材、讲义等均可）
3. 勾选需要提取的内容类型，选择详细程度
4. 点击「✨ 开始总结」，等待 AI 处理
5. 结果可直接复制，或点击「📝 转为排版笔记 →」衔接排版流程

---

## 🆓 免费额度说明

| 资源 | 免费额度 |
|------|---------|
| Cloudflare Workers 请求 | 每天 **10 万次** |
| Cloudflare KV 读操作 | 每天 **10 万次** |
| Cloudflare KV 写操作 | 每天 **1000 次** |
| Cloudflare Pages 带宽 | 每月 **500GB** |
| Groq API 调用 | 每天免费额度（足够个人使用） |

---

## 📄 License

MIT
