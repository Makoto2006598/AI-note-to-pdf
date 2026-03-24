# 本地模型部署指南（MacBook Air M4 16GB）

## 推荐模型

| 模型 | 大小 | 适用场景 | 速度（M4） |
|------|------|----------|-----------|
| `qwen2.5:7b` | ~4.7GB | **推荐首选**，中文理解好，格式遵循强 | ~30 tok/s |
| `qwen2.5:14b` | ~9.3GB | 质量更高，内存占用约 11GB | ~15 tok/s |
| `llama3.2:3b` | ~2.0GB | 极速测试用，格式遵循稍弱 | ~80 tok/s |
| `gemma3:4b` | ~3.2GB | 备选，英文更强 | ~50 tok/s |

> M4 16GB 统一内存：跑 7B 模型时系统剩余约 11GB，日常使用无压力。

---

## 第一步：安装 Ollama

```bash
# 官网安装（macOS）
brew install ollama

# 或直接下载安装包：https://ollama.com/download
```

验证安装：
```bash
ollama --version
```

---

## 第二步：拉取模型

```bash
# 推荐（中文笔记场景）
ollama pull qwen2.5:7b

# 可选：更高质量
ollama pull qwen2.5:14b

# 可选：速度最快
ollama pull llama3.2:3b
```

---

## 第三步：启动本地代理服务器

将项目解压后，在项目根目录运行：

```bash
# 默认使用 qwen2.5:7b，端口 8787
node local-proxy.js

# 切换模型
OLLAMA_MODEL=qwen2.5:14b node local-proxy.js

# 切换端口（如果 8787 被占用）
PORT=3000 node local-proxy.js
```

浏览器打开 http://localhost:8787 即可使用。

> **无需任何 API Key，完全离线运行。**

---

## 架构说明

```
浏览器
  │  访问 http://localhost:8787
  ▼
local-proxy.js（Node.js）
  │  ① 静态文件服务（自动替换 PROXY_URL）
  │  ② POST /api/convert → 转发给 Ollama
  ▼
Ollama（本地，11434 端口）
  │
  ▼
qwen2.5:7b / 其他模型
```

`local-proxy.js` 会在内存中将前端 JS 里的 `workers.dev` 地址替换为本地地址，
**无需修改或重新编译前端代码**。

---

## 方案二：用 Wrangler Dev（仅本地调试 Worker）

如果你需要调试 `worker.js` 本身：

```bash
# 在项目根目录创建 .dev.vars
echo "OLLAMA_URL=http://localhost:11434" > .dev.vars
# 如果同时需要 Groq：
echo "GROQ_API_KEY=gsk_xxx" >> .dev.vars

# 启动本地 Worker
npm install -g wrangler
npx wrangler dev

# Worker 在 http://localhost:8787/api/convert
```

前端将 `PROXY_URL` 改为 `http://localhost:8787/api/convert` 后运行：
```bash
cd notes-pdf
npm install
npm run dev  # http://localhost:5173
```

---

## 切换回 Groq 云服务

如果本地性能不够用，随时切回 Groq：

1. 前端直接访问线上版：https://notes-pdf.pages.dev
2. 或者只用 `wrangler dev` + `GROQ_API_KEY` 调试

---

## 常见问题

**Q：Ollama 报 "model not found"**
```bash
ollama pull qwen2.5:7b   # 重新拉取
ollama list              # 查看已有模型
```

**Q：端口 8787 被占用**
```bash
PORT=3000 node local-proxy.js
```

**Q：生成质量不理想**
- 升级到 `qwen2.5:14b` 效果更好
- 在 `local-proxy.js` 的 `PROMPTS` 里调整系统提示词

**Q：生成很慢**
- M4 跑 7B 约 30 tok/s，一篇笔记约 10-30 秒，属正常
- 改用 `llama3.2:3b` 可提升到约 80 tok/s
