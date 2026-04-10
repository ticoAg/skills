#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

REQ_CANDIDATES = [
    "IMPL_PLAN.md",
    "ROADMAP.md",
    "SPEC.md",
    "docs/roadmap.md",
    "docs/spec.md",
    ".task/",
    "tasks/",
]

DOC_LAYER_CANDIDATES = {
    "engineering": [
        "docs/engineering/README.md",
        "docs/engineering.md",
        "docs/dev/README.md",
    ],
    "architecture": [
        "docs/architecture/README.md",
        "docs/architecture.md",
        "docs/adr/README.md",
        "docs/decisions/README.md",
    ],
    "process": [
        "docs/process/README.md",
        "docs/superpowers/README.md",
        "docs/archive/README.md",
        "docs/plans/README.md",
    ],
}


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect_repo_name(root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    package_json = root / "package.json"
    if package_json.exists():
        name = read_json(package_json).get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("name ="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    return root.name


def existing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    found = []
    for rel in paths:
        target = rel.rstrip("/")
        if (root / target).exists():
            found.append(rel)
    return found


def detect_requirement_sources(root: Path) -> list[str]:
    found = existing_paths(root, REQ_CANDIDATES)
    if not found and (root / "README.md").exists():
        found.append("README.md")
    return found


def detect_doc_layers(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for layer, candidates in DOC_LAYER_CANDIDATES.items():
        for rel in candidates:
            if (root / rel).exists():
                found[layer] = rel
                break
    return found


def render_navigation_rows(root: Path, with_linear: bool) -> str:
    doc_layers = detect_doc_layers(root)
    rows = [
        ("项目定位与现状", "`README.md`"),
        ("Skill 选择与多代理路由", "`docs/agent-skill-routing.md`"),
        ("Agent 文档入口", "`docs/README.md`"),
    ]
    if "engineering" in doc_layers:
        rows.append(("工程实现规则", f"`{doc_layers['engineering']}`"))
    if "architecture" in doc_layers:
        rows.append(("业务 / 系统架构", f"`{doc_layers['architecture']}`"))
    if "process" in doc_layers:
        rows.append(("过程 / 阶段档案", f"`{doc_layers['process']}`"))
    optional = [
        ("需求 / 规划真源", "IMPL_PLAN.md"),
        ("任务清单与进度", ".task/"),
    ]
    for label, rel in optional:
        if (root / rel.rstrip("/")).exists():
            rows.append((label, f"`{rel}`"))
    if with_linear:
        rows.append(("Linear 工具链说明", "`docs/dev-toolchain/linear.md`"))
    return "\n".join(f"| {label} | {path} |" for label, path in rows)


def render_ssot_lines(root: Path, with_linear: bool) -> str:
    lines = []
    doc_layers = detect_doc_layers(root)
    if (root / "README.md").exists():
        lines.append("- **项目入口与现状**：`README.md`")
    requirement_sources = detect_requirement_sources(root)
    if requirement_sources:
        lines.append("- **需求 / 路线图 / 阶段目标**：" + "、".join(f"`{item}`" for item in requirement_sources))
    if "engineering" in doc_layers:
        lines.append(f"- **工程最佳实践与实现规则**：`{doc_layers['engineering']}`")
    if "architecture" in doc_layers:
        lines.append(f"- **业务边界与系统架构**：`{doc_layers['architecture']}`")
    if "process" in doc_layers:
        lines.append(f"- **过程档案 / 阶段记录**：`{doc_layers['process']}`")
    if (root / "docs").exists():
        lines.append("- **长期维护文档**：`docs/`")
    if with_linear:
        lines.append("- **项目管理与协作节奏**：`docs/dev-toolchain/linear.md` 与实际 Linear workspace / team 配置")
    if not lines:
        lines.append("- **项目入口与现状**：按仓库真实 README / docs / roadmap 补充")
    return "\n".join(lines)


def render_agents(root: Path, repo_name: str, with_linear: bool) -> str:
    doc_layers = detect_doc_layers(root)
    boundary_notes = []
    if "engineering" in doc_layers:
        boundary_notes.append(f"`{doc_layers['engineering']}` 承接工程最佳实践")
    if "architecture" in doc_layers:
        boundary_notes.append(f"`{doc_layers['architecture']}` 承接业务或系统架构")
    if "process" in doc_layers:
        boundary_notes.append(f"`{doc_layers['process']}` 承接计划或阶段档案")
    doc_boundary = ""
    if boundary_notes:
        doc_boundary = "\n- Keep document boundaries explicit: " + "；".join(boundary_notes) + "；不要把这些内容写进 agent 层。"
    linear_note = "\n- 若仓库采用 Linear 管理任务状态，先读 `docs/dev-toolchain/linear.md`；实际读写仍使用专门的 `linear` skill 或 MCP。" if with_linear else ""
    linear_red = "\n- 不把 Linear 中的计划状态写成仓库已实现事实；以代码、文档和验证证据为准" if with_linear else ""
    return f'''---
language: zh
type: AI Coder Guide Doc
note: Agent-facing repo entry guide focused on collaboration behavior, not business logic.
---

# {repo_name} Agent Entry

This file is the repo-level entry guide for agent collaboration. It should define only how agents work in this repo, not the repo's business-domain architecture.

## Navigation

| Need to know... | Read... |
|---|---|
{render_navigation_rows(root, with_linear)}

## Core Principles

Evidence first · Progressive disclosure · Small diff first · Verify before done · Agent layer stays business-agnostic

## Repo SSOT

{render_ssot_lines(root, with_linear)}

## Agent Behavior

- Read context before acting: inspect the active-scope `AGENTS.md`, the most relevant README / docs, and existing collaboration guidance before choosing an implementation path.
- Choose the workflow before writing code: for any non-trivial task, determine the right process skill / workflow first rather than coding immediately.
- Prefer small, reviewable diffs; avoid incidental refactors, broad renames, and repo-wide formatting unless explicitly required.
- Use progressive disclosure in communication: report conclusions, impact, verification, and next steps first; avoid dumping raw logs or long internal reasoning.
- Never claim completion without evidence. If verification is incomplete, state what is unverified, why, and how to reproduce the check.{doc_boundary}

## Tool Behavior

- Prefer read-first exploration before write operations.
- Prefer deterministic, repeatable commands and explicit working directories.
- Do not use destructive git operations unless explicitly requested.
- When a repo-specific script or command exists, prefer it over ad-hoc one-off commands.

## Skill 决策入口

- 开始任何非琐碎任务前，先根据 `docs/agent-skill-routing.md` 判断本轮应先使用哪类 skill。
- 默认顺序：先流程型 skill，再领域型 skill，最后协作 / 收尾型 skill。
- 准备宣称完成前默认补 `verification-before-completion`。{linear_note}

## Multi-Agent Collaboration

- Only use multi-agent execution when subproblems are actually independent.
- Keep orchestration, integration, conflict handling, unified verification, and final delivery in the main agent.
- Use `docs/agent-skill-routing.md` as the repo-level single source of truth for collaboration-skill routing.

## Instruction Priority

系统安全策略 > 用户当轮指令 > 最近的 `AGENTS.md` > 根级 `AGENTS.md` > `docs/` / `README.md`

## Red Lines

- 不提交密钥、密码、token、PII 或未脱敏配置
- 错误必须可见，不允许静默吞错或伪造结果
- 不执行破坏性回滚（`git reset --hard`、`git checkout --`）；未经明确要求不 push
- 不把规划中的能力写成“当前事实”
- 无法验证时必须写出未验证项、原因及可复现命令{linear_red}

## Delivery

- 最终回复包含：改了什么 / 为什么、影响范围、如何验证、回滚点
- 若本轮未完成，明确说明当前进度、下一步、已验证项与阻塞 / 风险
- 引用文件时使用可定位路径
'''


def render_skill_routing() -> str:
    return '''# Agent Skill Routing Guide

> Goal: help agents decide which skill to use first, which one to layer next, and when to move into multi-agent collaboration.

This file complements root `AGENTS.md`. It answers one narrower question: which skill-driven route should drive the current task?

## 1. Core Routing Principles

- Choose **process skills** first, **domain skills** second, then **collaboration / finishing skills**.
- A normal task should usually activate only 2 to 4 primary skills. Do not stack every possible skill.
- Decide **how to work** before deciding **what to implement**.
- Very small read-only questions or one-shot command checks do not need a full skill chain.
- Before claiming completion, default to `verification-before-completion`.

## 2. Default Skill Order

### 2.1 Process Skills

| Situation | Preferred skill | Why |
|---|---|---|
| New feature, behavior change, scope not fully settled | `brainstorming` | Converge on goal, constraints, and success criteria before implementation |
| Larger task, cross-module work, staged dependencies | `writing-plans` | Break work into executable steps with files, tests, and verification |
| Long-running work that benefits from resumable tracking | `planning-with-files` | Keep persistent planning artifacts for handoff and recovery |
| Bug, regression, unclear failure, unstable behavior | `systematic-debugging` | Reproduce, isolate root cause, validate hypotheses before patching |
| Review comments or requested follow-up changes | `receiving-code-review` | Judge whether feedback is valid and what scope it affects |

### 2.2 Domain Skills

Add the narrowest domain skill that matches the task's actual needs.

| Situation | Example skills |
|---|---|
| Frontend / UI work | `frontend-design`, `ui-design-brain`, `vercel-react-best-practices` |
| Accessibility / motion / polish | `fixing-accessibility`, `fixing-motion-performance`, `baseline-ui`, `make-interfaces-feel-better` |
| Python readability-only refactor | `code-simplifier-py` |
| TypeScript / JavaScript readability-only refactor | `code-simplifier-ts` |
| Architecture / technical docs / diagrams | `docs-with-mermaid` |
| OpenAI product / API guidance | `openai-docs` |
| Linear project management | `linear` |

### 2.3 Collaboration Skills

| Situation | Skill | Use for |
|---|---|---|
| Multiple independent subproblems can run in parallel | `dispatching-parallel-agents` | Split by independent domains or non-overlapping write scopes |
| There is already a clear implementation plan | `subagent-driven-development` | Execute plan tasks with workers/reviewers while main agent integrates |
| Plan should be executed sequentially in the current session | `executing-plans` | Follow plan order with checkpoints |

### 2.4 Finishing Skills

| Situation | Skill | Use for |
|---|---|---|
| Major work finished and a deliberate review pass is needed | `requesting-code-review` | Get another review layer before merge or handoff |
| About to say 'done' | `verification-before-completion` | Run verification first, then report results |
| User explicitly asks for a commit | `git-commit` | Consistent staging and conventional commit shaping |

## 3. Quick Decision Checklist

Before starting any non-trivial task, quickly ask:

1. Is this a new feature, a behavior change, or a bug fix?
2. Is the scope already clear, or should `brainstorming` happen first?
3. Will this span multiple stages or modules, making `writing-plans` or `planning-with-files` appropriate?
4. What is the narrowest domain skill that actually helps this task?
5. What verification is required before entering `verification-before-completion`?

## 4. Anti-Patterns

- Do not skip process skills just because the task 'looks small'.
- Do not activate multiple overlapping domain skills without a clear gap each one fills.
- Do not patch a bug before evidence supports the fix direction.
- Do not use multi-agent execution on tightly coupled work.
- Do not treat `verification-before-completion` as optional.
'''


def render_docs_readme(root: Path, repo_name: str, with_linear: bool) -> str:
    doc_layers = detect_doc_layers(root)
    linear_line = "\n- `docs/dev-toolchain/`：可选的 agent toolchain 文档，例如 Linear" if with_linear else ""
    linear_row = "\n| [dev-toolchain/linear.md](dev-toolchain/linear.md) | Linear 项目管理与 agent 协作约定 |" if with_linear else ""
    linear_section = "\n### 放进 `dev-toolchain/`\n\n- 项目管理工具链（如 Linear）的接入方式\n- 状态映射、节奏约定、协作边界\n- toolchain 只定义协作层，不替代代码和验证事实\n" if with_linear else ""
    adjacent_lines = []
    if "engineering" in doc_layers:
        adjacent_lines.append(f"- 工程最佳实践继续放在 `{doc_layers['engineering']}` 或同类位置")
    if "architecture" in doc_layers:
        adjacent_lines.append(f"- 业务或系统架构继续放在 `{doc_layers['architecture']}` 或同类位置")
    if "process" in doc_layers:
        adjacent_lines.append(f"- 计划、迁移和阶段记录继续放在 `{doc_layers['process']}` 或同类位置")
    adjacent_section = ""
    if adjacent_lines:
        adjacent_section = "\n### 邻接但不属于 agent 层的文档\n\n" + "\n".join(adjacent_lines) + "\n\n- agent 文档只负责协作入口、skill 路由和交付边界，不替代这些项目文档\n"
    return f'''# Agent Docs Portal

这里是 {repo_name} 的 agent 文档入口，用来统一回答四个问题：

1. agent 进入这个仓库时先看什么
2. skill 应该怎么选
3. agent 相关规则应该放到哪里
4. 可选的协作工具链文档放在哪里

## 一页看懂

- `AGENTS.md`：repo 级 agent 入口与高层规则
- `docs/agent-skill-routing.md`：skill 选择规则
- `docs/README.md`：本入口文档{linear_line}

## 推荐阅读路径

1. [../README.md](../README.md)
2. [../AGENTS.md](../AGENTS.md)
3. [agent-skill-routing.md](agent-skill-routing.md)

## 文档目录

| 文档 / 目录 | 定位 |
|---|---|
| [../AGENTS.md](../AGENTS.md) | repo 级 agent 入口、红线、交付口径 |
| [agent-skill-routing.md](agent-skill-routing.md) | skill 选择顺序、多代理协作路由 |
| [README.md](README.md) | agent 文档入口与放置规则 |{linear_row}

## 如何放置信息

### 放进 `AGENTS.md`

- 高层 agent 行为规范
- 红线、交付口径、工具使用原则
- 入口级导航

### 放进 `docs/agent-skill-routing.md`

- process / domain / collaboration / finishing skill 路由
- skill 选择 checklist 与 anti-patterns

### 放进 `docs/README.md`

- 这组 agent 文档的入口与分层说明
- 这些文档分别负责什么
{linear_section}
{adjacent_section}
## 文档维护规则

- 新增或修改 agent 文档时，保持几份文档职责边界清晰
- 不要把工程最佳实践、业务架构和过程档案混进这组 agent 文档里
- 若规则需要 project-specific 事实，请保持最小必要引用，不要让 agent 层膨胀成项目总说明

## 快速自检

```bash
rg -n "agent-skill-routing" docs/ --type md
rg "\\.\\./" docs/ --type md
```
'''


def render_linear_doc(repo_name: str) -> str:
    return f'''# Linear 作为 Agent Toolchain

本文档定义如何把 Linear 纳入 {repo_name} 的 agent 协作工具链。

## 目标

- 让需求、issue、cycle、project 的状态有统一入口
- 让 agent 在读写 Linear 时知道哪些信息属于协作真源，哪些信息仍以仓库事实为准
- 避免‘Linear 已完成’与‘代码 / 文档事实已完成’之间的语义漂移

## 推荐边界

- **Linear 负责**：任务状态、负责人、优先级、里程碑、周期、讨论串
- **仓库代码负责**：真实实现事实
- **仓库文档负责**：规则、说明和交付证据
- **Agent 文档负责**：协作规则与执行路径

## 推荐约定

1. 需求拆解后在 Linear 中维护 issue / project / cycle
2. 代码改动完成后，再回写 Linear 状态，不反过来以 Linear 替代实现事实
3. agent 需要读写 Linear issue / project 时，使用专门的 `linear` skill 或 Linear MCP 工具

## 交付口径

- ‘Linear 已完成’ 不等于 ‘代码已完成’
- 最终交付仍应包含代码证据、文档更新和必要说明
'''


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def materialize_target(root: Path, rel_path: str, content: str, write_mode: str, draft_dir: Path) -> tuple[str, str]:
    target = root / rel_path
    existed = target.exists()
    if write_mode == "overwrite":
        write_file(target, content)
        return rel_path, "overwritten" if existed else "created"
    if write_mode == "draft":
        draft = draft_dir / rel_path
        write_file(draft, content)
        return rel_path, f"draft:{draft.relative_to(root)}"
    if existed:
        draft = draft_dir / rel_path
        write_file(draft, content)
        return rel_path, f"draft:{draft.relative_to(root)}"
    write_file(target, content)
    return rel_path, "created"


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap agent-only repo guidance docs.")
    parser.add_argument("repo_root", help="Path to the target repository root")
    parser.add_argument("--repo-name", help="Explicit repo display name")
    parser.add_argument("--with-linear", action="store_true", help="Also scaffold Linear toolchain docs")
    parser.add_argument("--write-mode", choices=["safe", "draft", "overwrite"], default="safe")
    parser.add_argument("--draft-dir", default=".agent-native-bootstrap", help="Draft output dir for safe/draft modes")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"repo root does not exist or is not a directory: {root}")

    repo_name = detect_repo_name(root, args.repo_name)
    draft_dir = root / args.draft_dir

    files = {
        "AGENTS.md": render_agents(root, repo_name, args.with_linear),
        "docs/agent-skill-routing.md": render_skill_routing(),
        "docs/README.md": render_docs_readme(root, repo_name, args.with_linear),
    }
    if args.with_linear:
        files["docs/dev-toolchain/linear.md"] = render_linear_doc(repo_name)

    results = [materialize_target(root, rel, content, args.write_mode, draft_dir) for rel, content in files.items()]

    print(f"Bootstrapped agent docs for: {repo_name}")
    print(f"Write mode: {args.write_mode}")
    print("Results:")
    for rel, status in results:
        print(f"  - {rel}: {status}")
    if args.write_mode in {"safe", "draft"}:
        print(f"Draft directory: {draft_dir}")
    print("Next step: review generated files and replace generic placeholders with repo-specific collaboration facts.")


if __name__ == "__main__":
    main()
