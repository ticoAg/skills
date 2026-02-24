---
name: brief2flow
description: Define how an agent should initialize or optimize workflow blueprint docs in Markdown (workflow.blueprint.md) for a workflow workspace directory (under your configured workspace root, e.g. $POI_COZE_WORKSPACE_ROOT/WORKFLOW_ID/). Emphasize an abstract-style summary, a safe Mermaid flowchart, Node.* numbered node specs, backticked types, fenced ```markdown prompts, and traceable I/O variables with descriptions. Use Markdown-first and add Extractor LLM stages only when downstream needs strict structured fields.
---

# brief2flow 蓝图约定（workflow.blueprint.md）

## Overview

本 Skill 定义的是：**Agent 如何把用户的自然语言创作需求（brief）落地为可执行的工作流蓝图（blueprint）**。

它与 `brief2flow` CLI 的目标一致：把 workflow 的“可编辑解构面”收敛为一个人类友好的 `workflow.blueprint.md`，用于 review / diff / 协作编辑，并支持“按需”再展开为更结构化的输入或 workspace 文件。

核心策略：
- **Markdown-first**：用 Markdown/纯文本承载策略与生成要求（更自然、效果更好、字段更少）。
- **按需结构化**：仅当下游节点必须吃结构化字段时，追加 **Extractor LLM** 从上一步 Markdown 中提取少量严格 JSON 字段。

本 Skill 支持两种模式：
- **初始化**：workspace 还没有 `workflow.blueprint.md`（或为空）→ 生成一份符合约定的 `workflow.blueprint.md`。
- **优化**：已有 `workflow.blueprint.md` 初稿 → 按约定补齐/修复（尽量小 diff）。

---

## 核心约定（必须遵守）

### 0) 蓝图开头必须是“摘要”（Abstract-style）
蓝图文件开头的“目标/介绍”写成论文摘要风格的简要概述：**基于用户需求 + 实际实现方案**。

要求：
- 标题（H1）之后必须紧跟 `## 摘要`。
- `## 摘要` 至少包含下面 4 类信息（可用 bullet list）：
  - **用户需求**：用户要解决什么问题、面向谁、输入是什么。
  - **实现方案**：用哪些关键步骤/节点把需求落到可执行流程（点到为止）。
  - **产出**：本 workflow 会输出哪些结果变量（文本/图片/视频/对象等），不规定数量。
  - **约束/假设**：不可编造的事实边界、合规/品牌/素材来源等硬约束。

### 1) Markdown-first（质量优先）
- 文本生成节点优先输出 **Markdown/纯文本**（例如：`strategy_brief_md`、`copy_pack_md`、`video_prompt_md`）。
- 避免让 LLM 直接输出“深层 JSON + 超多字段”。需要结构化时，用 Extractor 从 Markdown 提取。

### 2) 视频细节不拆字段
- 运镜/转场/特效/色彩/光影/节奏等要求：统一写进“视频脚本/视频提示词”自然语言中。

### 3) Node 命名与排版规范
- 节点名称必须以 `Node.` 开头：`Node.0`、`Node.1`、`Node.2`…
- `workflow.blueprint.md` 必须包含：
  - 一段 **Mermaid** 流程图（只写整体节点流程）
  - 每个节点的：名称（带序号）、类型、功能（简述）、输入/输出（开始仅输入、结束仅输出）、prompt/代码
- 类型必须使用反引号包裹，例如：`文本生成`、`文本生成（Extractor）`、`图片生成`、`视频生成`、`开始`、`结束`。
- prompt 必须使用围栏包裹：
  - 文本生成：```markdown
  - 代码执行：```bash 或 ```python（按实际）

### 4) 变量 I/O 必须“可追溯 + 可复用”
对每个节点（Node）的变量 I/O，按下面要求写清（**必选项缺一不可**）：

**特殊规则（开始/结束节点）：**
- `开始` 节点：只写 `**输入**`（不在开始节点重复声明 `**输出**` 变量；下游可直接引用这些入参）。
- `结束` 节点：只写 `**输出**`（不在结束节点重复声明 `**输入**` 变量；在输出注释中写清来自哪个上游节点以保持可追溯）。

**变量名长度限制：**
- 变量名**最长不能超过 20 字符**（建议使用简短且具有明确含义的 `snake_case` 缩写）。

**输入变量（Node 的 `**输入**` 部分）必选：**
- 变量名（必须遵守长度限制）
- 类型（string/image/video/object…）
- 来源（必填）
- 注释说明（必填，一句话说明用途/关键约束/为空策略等）

**输入的 JSON 示例（必选）：**
- 必须在 `**输入**` 列表中提供一个 `**示例**` 字段，附带 JSON 代码块。要求：
  - “可选”类型的属性或参数，默认值应为空字符串 `""`。
  - **绝不允许出现 `None`**（非 Python 风格，应使用合法 JSON 或 `""`）。
  - 最多只允许三层嵌套结构，保持精简。

**输入变量的默认值（可选）：**
- 默认值：仅当存在且重要时写；不强制要求每个变量都有默认值

**输出变量（Node 的 `**输出**` 部分）必选：**
- 变量名（必须遵守长度限制）
- 类型
- 注释说明（必填）

> 推荐写法（示例，不强制逐字一致；但“类型/来源/注释”三要素必须齐全）：
> - 上游变量引用：`- \`x\`（string）← 来自「Node.1 ...」.\`y\`：用于……（默认：... 可选）`
> - 用户输入（开始节点常见）：`- \`poi\`（string，来源：用户输入）：……（默认：... 可选）`
> - 常量/手填：`- \`lang\`（string，来源：常量，可选）：……（默认：... 可选）`
> - **示例**：
>   ```json
>   {
>     "x": "...",
>     "poi": "...",
>     "lang": ""
>   }
>   ```
> - 工作流输出（结束节点常见）：`- \`result_md\`（string）← 来自「Node.2 ...」：作为 workflow 对外返回值`

### 5) Mermaid 安全规范（避免解析报错）
- 必须用 `flowchart TD`
- 节点文本用 `["..."]`（带引号）
- Mermaid label 使用“纯文本 + 空格/短横线”表达节点含义，以提高解析兼容性（例如 `文本生成 Extractor`、`视频生成 image2video`）
- 推荐避免在 Mermaid label 中使用括号与 HTML 换行（例如 `(` `)`、`<br/>`）
- **简化跨节点连线（线性优先）**：Mermaid 流程图应聚焦于**核心执行路径**。同一链路上的后置节点可隐式获取所有前置节点生成的变量。**禁止绘制繁杂的跨节点变量引用连线**（例如把 `Node.1` 的输出连给 `Node.4`、`Node.5`、`Node.6`），以保证连线清晰、不相互缠绕。

### 6) Extractor 节点（严格 JSON，小 schema）
- Extractor 节点类型：`文本生成（Extractor）`
- 输入：上一步 Markdown（`*_md`）
- 输出：严格 JSON，且只能二选一：
  - 成功：`{"image_prompt":"..."}` / `{"video_prompt":"..."}`
  - 失败：`{"error":"MISSING_..."}`（错误码固定）
- 输出字段聚焦“下游要用的字段”，保持 schema 小而稳定。

---

## 节点类型与输入能力（通用枚举）

> 说明：这里的“类型”是写进 `workflow.blueprint.md` 的**描述性类型**（用于人读与手工同步到 Coze），不要求与 workspace YAML 的 `type:` 字段一一对应。

### 常用核心类型（推荐优先掌握）

#### `开始`
- **功能**：声明 workflow 入参（启动时需要用户提供的变量）。
- **支持输入**：文本字段为主（string/number/bool 等）。
- **变量约定**：开始节点只声明 `**输入**` 变量（不重复声明 `**输出**`）；下游可直接引用这些入参。

#### `结束`
- **功能**：声明 workflow 返回值（对外暴露哪些变量）。
- **变量约定**：结束节点只声明 `**输出**` 变量（不重复声明 `**输入**`）；在输出注释里写清来自哪个上游节点以保持可追溯。

#### `文本生成`（LLM）
- **功能**：理解输入并执行“文本里定义的任务”，生成文本或结构化内容。
- **支持输入（模态）**：
  - 文本（必有其一）
  - 图片（可选）：用于理解画面、对齐风格、做参考
  - 视频（可选）：用于理解内容、节奏、镜头语言等
- **典型输出**：
  - 推荐：Markdown/纯文本（质量更好、字段更少、便于审阅与迭代）
  - 可选：严格 JSON（仅当下游必须结构化时使用）
- **写法要点（文本输入内容）**：文本通常包含“任务 + 输出要求/约束 + 事实边界（如有）”。

#### `文本生成（Extractor）`（LLM 的特化用法）
- **功能**：从上一步 Markdown/纯文本中按需提取结构化字段（最小 schema）。
- **支持输入（模态）**：文本（Markdown/纯文本）。
- **输出约束（必须）**：
  - 只输出严格 JSON（不输出 Markdown/解释/代码块）
  - schema 极小，只包含下游要用的字段
  - 失败时只输出 `{"error":"MISSING_..."}`（错误码固定）

#### `图片生成`
- **功能**：根据文本描述生成图片；或参考输入图片进行风格/内容调整再生成。
- **支持输入（模态）**：
  - 文本（必有其一）：对想要的图片做全方位描述（主体、构图、光影、风格、细节、禁用元素等）
  - 图片（可选）：作为参考图/改图依据
- **典型输出**：图片（单张或多张，取决于节点参数）。
- **写法要点（文本输入内容）**：把画面要求写全（主体、场景、镜头感、光影、材质、氛围、质量要求等），避免拆成过多字段。

#### `视频生成`
- **功能**：根据文字描述与可选参考模态生成视频。
- **支持输入（模态）**：文字、图片、视频、音频都可选，但**不能全部为空**；通常为“文本 + 其他任意模态”组合。
- **典型输出**：视频。
- **常见子模式（描述用，不强绑定厂商命名）**：
  - **参考生成**：单参考（图片/视频/音频之一）+ 文本（可选但推荐）
  - **首尾帧**：双图（首帧/尾帧）+ 文本
- **写法要点（文本输入内容）**：比图片更专业，覆盖：镜头语言/运镜、节奏、画面风格、光影、色彩、主体运动、转场、声音/氛围（如适用）；尽量写成可直接喂模型的一段描述。

#### `代码执行`
- **功能**：用确定性逻辑做数据处理（校验、清洗、拼装、解析、抽取、格式化、打包等）。
- **支持输入**：文本/结构化对象（按代码定义）。
- **典型输出**：文本或结构化对象（按代码定义）。

### 常见扩展类型（来自 Coze 节点面板，非穷举）

> 完整条目（含 `data-node-type` 数字与中文名称）见：`references/coze-node-types.md`。
> 这些类型的“真实 I/O”往往依赖具体节点参数或插件定义；在 `workflow.blueprint.md` 中仍可按统一格式描述其输入/输出与用途。

常见类别（按面板名称归类）：
- 插件类：插件 / 更多图像插件 / 抠图 / 提示词优化 / 画质提升（I/O 依插件而定）
- 流程控制：选择器 / 循环 / 批处理 / 异步任务 / 工作流（子流程）
- 变量与数据：变量赋值 / 变量聚合 / 文本处理 / 输入 / 输出
- 数据与接口：HTTP 请求 / SQL 自定义 / 新增数据 / 更新数据 / 查询数据 / 删除数据
- JSON 工具：JSON 序列化 / JSON 反序列化
- 知识与记忆：知识库检索 / 知识库写入 / 知识库删除 / 长期记忆写入 / 长期记忆检索
- 音视频工具：视频抽帧 / 视频提取音频
- 会话消息类：创建会话 / 修改会话 / 删除会话 / 查询会话列表 / 查询会话历史 / 清空会话历史 / 创建消息 / 修改消息 / 删除消息 / 查询消息列表

---

## 初始化：参数与拓扑（通用）

### 1) 初始化前先锁定的“可变参数”
本 Skill 不内置具体业务默认值；当用户未明确给出时，优先：
1) 从现有 workspace（`workflow/nodes/*.yaml` 与 `workflow/prompts/*.md`）**推导**现有产出与约束；
2) 仍无法推导时，再向用户确认（而不是擅自设定）。

通常需要确认的参数（示例清单，按需取用）：
- 产出范围：是否需要文案/图片/视频，是否三路都要
- 产出数量：文案/图片/视频各要几份（以及是否需要多版本）
- 视频模式：text2video / image2video；是否需要参考图/首帧一致
- 语言与受众：中文/英文/双语；面向站点/投放/社媒
- 输入信息：是否增加可选 `poi_context`（事实信息/禁忌），用于降低“编造事实”风险

### 2) 参考拓扑（按需裁剪）
如果需求是“同源分析 → 文案/图片/视频三路产出”，可使用以下参考拓扑，并在 `workflow.blueprint.md` 中用 Node 编号表达：
1) `Node.0` 开始：输入（例如 `poi` / `target_audience`，可选 `poi_context`）
2) `Node.1` 策略简报MD（同源分析）：输出 `strategy_brief_md`
3) 文案链（可选）：
   - `Node.2` 文案生成MD：输出 `copy_pack_md`
4) 图片链（可选）：
   - `Node.3` 图片提示MD：输出 `image_prompt_md`
   - `Node.3.5` Extractor 提取：输出 `image_prompt`（严格 JSON 小 schema）
   - `Node.4` 图片生成：输出 `hero_image`（或 `images[]`）
5) 视频链（可选）：
   - `Node.5` 视频脚本+提示MD：输出 `video_prompt_md`
   - `Node.5.5` Extractor 提取：输出 `video_prompt`（严格 JSON 小 schema）
   - `Node.6` 视频生成：输出 `video`（必要时使用 `hero_image` 作为首帧/参考图）
6) `Node.7` 结束：返回需要对外暴露的变量（analysis/copy/image/video 等）

Extractor 的最小 schema 示例（仅示例，不代表必须字段）：
- `{"image_prompt":"..."}`
- `{"video_prompt":"..."}`
- 失败：`{"error":"MISSING_IMAGE_PROMPT"}` / `{"error":"MISSING_VIDEO_PROMPT"}`

---

## 执行步骤（初始化/优化通用）

1) 定位目标 workspace：在你配置的 workspace root 下（例如 `$POI_COZE_WORKSPACE_ROOT/WORKFLOW_ID/`）。
2) 只读探索（必要时）：
   - `workflow/global.yaml`（edges）
   - `workflow/nodes/*.yaml`（已有节点类型与变量命名）
   - `workflow/prompts/*.md`（已有 prompt 约束与意图）
3) 写入或更新 `workflow.blueprint.md`（包含：摘要 + Mermaid + 节点清单；聚焦“可编辑蓝图”，保持内容紧凑可读）。
4) 运行校验脚本并修复问题：
   - 优先：`python3 ~/.codex/skills/brief2flow/scripts/validate_blueprint_md.py <path-to-workflow.blueprint.md>`
   - 可选（在已安装/可导入 `brief2flow` 的环境中）：`uv run --project <path-to-brief2flow> python -m brief2flow.validate_blueprint_md <path-to-workflow.blueprint.md>`

仅当需要回包/导入 zip 时（非必须）：
- 用 `brief2flow verify --dir <workspace_dir>` 校验 workspace（若未安装，可用 `uv run --project <path-to-brief2flow> brief2flow verify --dir <workspace_dir>`）

---

## 资源
- `scripts/validate_blueprint_md.py`：对 `workflow.blueprint.md` 做基本一致性校验（Node 命名、Mermaid 安全规则、prompt 围栏等）。
- `scripts/extract_node_types_from_html.py`：从你复制的 Coze 节点面板 HTML（例如 `temp.html`）提取全量节点条目，更新 `references/coze-node-types.md`。
- `references/coze-node-types.md`：Coze 节点面板条目（全量、可追溯的“覆盖面”证据）。
