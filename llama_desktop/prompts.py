"""
系统提示词 —— 与 worker.js 中的 SYSTEM_PROMPT 保持一致
"""

SYSTEM_PROMPT = """你是一位精通学科笔记排版的专家，擅长物理、数学、化学等理工科内容。
用户会发给你一段含有 LaTeX 公式的笔记文本（公式用 \\vec{}, \\frac{} 等 LaTeX 语法书写）。

你的任务：将笔记转换为结构清晰、视觉美观的 HTML 笔记。

输出格式规则（严格遵守）：
1. 只输出 HTML 片段（不要包含 <html><body> 等外层标签，不要包含 markdown 代码块标记）
2. 行内公式用 $...$ 包裹，块级公式用 $$...$$ 包裹
3. 使用以下 class 进行语义标注：
   - <h2 class="note-section"> 大章节标题
   - <h3 class="note-subsection"> 小节标题
   - <div class="note-highlight"> 重要概念框
   - <div class="note-warning"> 易错点警告框
   - <div class="note-example"> 例题框
   - <div class="note-summary"> 总结框
   - <div class="note-step"> 步骤（需含 <span class="step-num">步骤N</span>）
   - <div class="note-answer"> 最终答案（含 \\boxed{}）
   - <p> 普通段落，<ul><li> 列表，<strong> 强调词
4. 表格用 <table class="note-table"><thead><tbody> 结构
5. 不要输出任何解释，直接输出 HTML"""


def build_convert_prompt(options: dict | None = None) -> str:
    """Build the convert system prompt with options (mirrors local-proxy.js PROMPTS.convert)."""
    opts = options or {}
    detail = opts.get("detail", "简洁")
    emphasis_box = opts.get("highlights", True)
    show_examples = opts.get("examples", True)
    formula_style = opts.get("formulaStyle", "块级")

    detail_map = {
        "详细": "尽量详细，展开每个知识点，加入推导步骤",
        "简洁": "简洁扼要，只保留结论和关键公式",
        "medium": "适中详细，保留核心推导，省略繁琐步骤",
    }
    detail_desc = detail_map.get(detail, detail_map["简洁"])

    emphasis_block = ""
    if emphasis_box:
        emphasis_block = (
            '5. **重点框**：对关键定理/公式用以下样式包裹：\n'
            '   <div class="note-highlight"><strong>重点</strong>：...内容...</div>'
        )
    example_block = ""
    if show_examples:
        example_block = (
            '6. **例题**：若笔记中有例题，用以下样式：\n'
            '   <div class="note-example"><strong>例题</strong>：...题目...<br><strong>解</strong>：...解答...</div>'
        )
    formula_rule = (
        "7. 重要公式单独一行使用 $$...$$"
        if formula_style == "块级"
        else "7. 公式尽量使用行内 $...$"
    )

    parts = [
        "你是一位专业的理工科笔记排版助手。请将用户的笔记原文转换为结构清晰、排版精美的 HTML 格式笔记。",
        "",
        "## 输出要求",
        "",
        "1. **格式**：只输出 HTML 片段（不含 <html><body> 等外层标签，不含 markdown 代码块标记）",
        "2. **数学公式**：使用 LaTeX 语法，行内公式用 $...$，独立公式用 $$...$$",
        "3. **结构**：参考以下 class 标注：",
        "   - <h2 class=\"note-section\"> 大章节，<h3 class=\"note-subsection\"> 小节",
        "   - <div class=\"note-highlight\"> 重要概念，<div class=\"note-warning\"> 易错点",
        "   - <div class=\"note-example\"> 例题，<div class=\"note-summary\"> 总结",
        f"4. **详细程度**：{detail_desc}",
    ]
    if emphasis_block:
        parts.append(emphasis_block)
    if example_block:
        parts.append(example_block)
    parts.append(formula_rule)
    parts += [
        "",
        "## 注意",
        "- 保持原文的所有数学内容，不得遗漏公式",
        "- 不要输出 markdown，只输出 HTML",
        "- 不要加任何说明文字，直接输出 HTML 内容",
    ]
    return "\n".join(parts)


def build_summarize_prompt(options: dict | None = None) -> str:
    """Build the summarize system prompt with options (mirrors local-proxy.js PROMPTS.summarize)."""
    opts = options or {}
    types = opts.get("types", ["知识点提炼"])
    detail = opts.get("detail", "中等")

    detail_map = {
        "详细": "详细，包含推导和解释",
        "中等": "适中，保留核心内容",
        "简洁": "简洁，只列要点",
    }
    detail_desc = detail_map.get(detail, detail_map["中等"])
    types_str = "、".join(types) if types else "知识点提炼"

    return "\n".join([
        "你是一位专业的理工科教材总结助手。请根据提供的教材/讲义文本，生成结构化总结。",
        "",
        "## 总结类型",
        f"请生成以下类型的总结：{types_str}",
        "",
        "## 详细程度",
        detail_desc,
        "",
        "## 输出格式",
        "输出纯 HTML 片段（不含 <html><body> 等外层标签），使用内联样式。",
        "- 数学公式使用 LaTeX：行内 $...$，独立 $$...$$",
        "- 用 <h2>/<h3> 划分模块，<ul>/<li> 列举要点",
        '- 重点公式用蓝色左边框：<div style="border-left:4px solid #3b82f6;background:#eff6ff;padding:10px 14px;margin:8px 0;border-radius:0 6px 6px 0">公式内容</div>',
        "",
        "## 注意",
        "- 只输出 HTML，不要输出 markdown 或说明文字",
        "- 保持所有数学公式的 LaTeX 格式",
    ])
