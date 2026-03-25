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
| 云端 AI | Groq / Claude / DeepSeek / 通义 / 智谱 / Kimi |
| 本地 AI | llama.cpp（llama-cpp-python，支持 Metal/CUDA） |
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
├── local-proxy.js          # 本地 Ollama 代理（Node.js）
├── llama_desktop/          # 本地 llama.cpp 桌面服务
│   ├── main.py             # 入口（GUI 或 --headless）
│   ├── gui.py              # Tkinter 桌面 GUI
│   ├── server.py           # FastAPI 本地 API 服务
│   ├── model_manager.py    # GGUF 模型加载管理
│   ├── prompts.py          # 系统提示词
│   └── requirements.txt
└── README.md
```

---

## 💻 本地模型离线使用（Qwen2.5-14B + llama.cpp）

> **无需任何 API Key，完全离线运行。**
> 适合已下载 GGUF 模型文件的用户，使用 `llama_desktop` 模块直接加载模型并在本地提供 API 服务。

---

### 前置条件

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 12+（Apple Silicon 原生支持 Metal GPU 加速） |
| Python | 3.10 或更高 |
| 内存 | 建议 16GB 以上（运行 14B Q4 模型约占用 10GB） |
| 模型文件 | `Qwen2.5-14B-Instruct` 的任意 GGUF 量化版本 |

**推荐量化版本（按内存占用排序）：**

| 量化版本 | 文件大小 | 内存占用 | 质量 | 推荐场景 |
|----------|----------|----------|------|----------|
| `Q4_K_M` | ~9.3 GB  | ~10 GB   | ★★★★ | **首选**，16GB 内存可用 |
| `Q5_K_M` | ~11 GB   | ~12 GB   | ★★★★★ | 质量更高，16GB 内存勉强可用 |
| `Q8_0`   | ~15 GB   | ~16 GB   | ★★★★★ | 需要 24GB+ |
| `Q3_K_M` | ~7.6 GB  | ~8.5 GB  | ★★★  | 内存不足时备选 |

---

### 第一步：将模型文件放到推荐目录

`llama_desktop` 启动时会自动扫描以下路径：

```
~/models/
~/.cache/lm-studio/models/
```

**建议操作：**
```bash
mkdir -p ~/models
mv ~/Downloads/qwen2.5-14b-instruct-q4_k_m.gguf ~/models/
```

> 也可以不移动文件，启动后在 GUI 中点击「浏览」手动选择任意位置的 `.gguf` 文件。

---

### 第二步：安装 Python 依赖

**macOS Apple Silicon（M1/M2/M3/M4）——启用 Metal GPU 加速：**

```bash
cd llama_desktop

# 先安装其他依赖
pip install fastapi uvicorn pydantic

# 编译安装 llama-cpp-python，开启 Metal 加速（重要！）
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --no-cache-dir
```

> ⚠️ 必须带 `CMAKE_ARGS="-DGGML_METAL=on"` 编译，否则只用 CPU，速度慢约 5 倍。
> 编译过程约 3～5 分钟，请耐心等待。

**验证 Metal 是否生效：**
```bash
python -c "from llama_cpp import Llama; print('llama-cpp-python 安装成功')"
```

---

### 第三步：启动桌面 GUI

```bash
# 在项目根目录执行
python llama_desktop/main.py
```

启动后会弹出如下界面：

```
┌─────────────────────────────────────────┐
│ 模型文件  [自动填充扫描到的路径] [浏览][扫描] │
│ 服务地址  127.0.0.1   端口  8788         │
│ GPU 层数  -1（= 全部交给 Metal）          │
│                                          │
│ [⚡ 加载模型 + 启动服务]  [🌐 在浏览器打开] │
│ ● 未启动                                 │
│ ┌──────────────────────────────────────┐ │
│ │ 日志输出区域                          │ │
└─────────────────────────────────────────┘
```

**操作步骤：**

1. **确认模型路径**
   GUI 启动时自动扫描 `~/models/`，若找到 `.gguf` 文件会自动填入。
   未找到时点击「扫描」或「浏览」手动选择文件。

2. **确认端口**
   默认端口 `8788`。若被占用可改为其他值（如 `8080`）。

3. **GPU 层数保持 `-1`**
   `-1` 代表将所有层全部 offload 到 Metal GPU，速度最快。
   若遇到内存不足报错，可改为 `20`～`35` 减少 GPU 占用。

4. **点击「⚡ 加载模型 + 启动服务」**
   日志区会显示加载进度，Q4_K_M 14B 模型首次加载约需 **10～30 秒**。
   看到 `API 服务已启动：http://127.0.0.1:8788/api/convert` 即表示就绪。

5. **点击「🌐 在浏览器打开」**
   自动在浏览器中打开本地前端界面，即可正常使用所有功能。

---

### 第四步：使用前端界面

浏览器打开后，界面与在线版完全相同。此时流量走向：

```
浏览器（notes-pdf/dist/index.html）
  │  POST /api/convert
  ▼
llama_desktop/server.py（127.0.0.1:8788）
  │  llama-cpp-python 推理
  ▼
Qwen2.5-14B-Instruct（本地 GGUF，Metal 加速）
```

> 前端默认请求 Cloudflare Worker 地址。`llama_desktop` 通过 `local-proxy` 的静态文件服务将该地址自动替换为本地地址，**无需修改任何代码**。
> 直接双击打开 `notes-pdf/dist/index.html` 时仍会请求云端 Worker，需通过 GUI 的「在浏览器打开」按钮才能正确走本地。

**性能参考（MacBook Air M4 16GB，Q4_K_M）：**

| 操作 | 耗时估算 |
|------|----------|
| 模型加载 | 10～30 秒（首次） |
| 笔记转换（1000 字） | 20～40 秒 |
| PDF 总结（5000 字） | 40～90 秒 |
| 生成速度 | 约 8～15 token/s |

---

### 无界面模式（headless）

适合 SSH 远程或脚本自动化场景：

```bash
# 指定模型路径，后台运行
python llama_desktop/main.py --headless \
  --model ~/models/qwen2.5-14b-instruct-q4_k_m.gguf \
  --port 8788

# 自定义所有参数
python llama_desktop/main.py --headless \
  --model ~/models/qwen2.5-14b-instruct-q4_k_m.gguf \
  --host 0.0.0.0 \   # 局域网可访问
  --port 8788 \
  --gpu 28            # 手动指定 GPU 层数
```

运行后按 `Ctrl+C` 停止服务。

---

### 常见问题

**Q：点击启动后日志显示 `ggml_metal_init: failed`**
```bash
# 重新安装，确保 Metal 编译标志正确
pip uninstall llama-cpp-python -y
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --no-cache-dir
```

**Q：报错 `Killed` 或内存不足**
- 换用 `Q3_K_M` 量化版本（约 8.5GB）
- 或将 GPU 层数从 `-1` 改为 `20`，减少显存占用

**Q：生成速度很慢（< 3 token/s）**
- 确认 Metal 已启用：日志中应有 `ggml_metal_init: GPU name: Apple M4`
- 若没有该行，说明 llama-cpp-python 未编译 Metal 支持，按上方步骤重装

**Q：端口 8788 已被占用**
```bash
# 换一个端口
python llama_desktop/main.py --headless --model ~/models/xxx.gguf --port 8080
```

**Q：浏览器打开后仍然请求云端 Worker**
- 必须通过 GUI 的「🌐 在浏览器打开」按钮，不能直接双击 `dist/index.html`
- 或手动访问 `http://127.0.0.1:8788`（需本地代理服务提供静态文件）

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
