---
name: office-content-extractor
description: Extract textual content from Word, Excel, PDF, and PowerPoint files in a general-purpose way. Use when Codex needs to design, review, or implement document content extraction workflows; choose between format conversion, plain text extraction, table-aware extraction, or page-level visual transcription; normalize outputs into stable text, markdown, or chunked content; or handle common office-document edge cases such as merged cells, mixed paragraph-table content, scanned PDFs, and presentation slides with images.
---

# Office Content Extractor

## Overview

Use this skill to design or refine a general `Word`、`Excel`、`PDF`、`PPT/PPTX` 内容提取方案。

目标很简单：稳定提取文件内容，不引入复杂业务逻辑，不假设行业模板，只关注“如何尽量完整、干净、可追溯地把内容取出来”。

## Core Rule

先判断文档结构，再选择提取方式；不要只按文件后缀决定实现。

优先回答这几个问题：

1. 文档主要是连续文本、表格，还是页面视觉内容。
2. 是否需要保留段落、sheet、页码、slide 顺序。
3. 是否需要 Markdown，而不仅是纯文本。
4. 原文件是否需要先转换成更适合提取的格式。

## Workflow

1. 先做格式归一化。
   对 `doc/ppt/xls` 这类旧格式，优先转成 `docx/pptx/xlsx/pdf`，再进入提取链路。

2. 识别文档主结构。
   连续文本为主时，优先文本提取。
   表格为主时，优先表格感知提取。
   页面视觉结构为主时，优先按页转写。

3. 选择提取路径。
   `Word`：段落与表格分流。
   `Excel`：按 sheet 读取，保留表格边界。
   `PDF`：在“文本提取”和“页面视觉转写”之间择优。
   `PPT`：在“元素级抽取”和“转 PDF 后按页转写”之间择优。

4. 标准化输出。
   统一成 `text`、`markdown` 或 `chunks`，并保留基础定位信息。

5. 做质量检查。
   检查是否丢页、乱序、空结果、超长块、脏格式和特殊图片失败。

## Format Guide

### Excel

适合按 sheet 提取。

- 优先保留 sheet 名
- 按行提取非空单元格
- 表格结构明显时，保留列关系或输出为 Markdown 表格
- 文件异常时先做 OOXML 或维度级防御

细节读 [references/excel-extraction.md](references/excel-extraction.md)。

### Word

适合按“段落流 + 表格流”提取。

- 段落按原顺序输出
- 表格单独处理，不要直接揉进纯文本
- 如果表格很重要，可以转 Excel 后复用表格提取逻辑

细节读 [references/word-extraction.md](references/word-extraction.md)。

### PDF / PPT

当页面视觉结构本身承载信息时，优先考虑页面级提取。

- 原生可提文本的 PDF：先尝试文本路径
- 扫描件 PDF：优先 OCR 或页面视觉转写
- 视觉强的 PPT：可转 PDF 后按页提取

细节读 [references/pdf-ppt-extraction.md](references/pdf-ppt-extraction.md)。

## Output Contract

优先统一为这些字段：

- `content`
- `source_format`
- `output_format`
- `page_number` 或 `sheet_name` 或 `slide_number`
- `chunk_index`
- `parser_strategy`

如果输出 Markdown，尽量保留：

- 段落分隔
- 表格边界
- 图片引用或占位
- 页或 slide 的天然顺序

如果输出 chunks，优先保证：

- 顺序稳定
- 单块不过长
- 元数据足够回溯原位置

## References

- 通用策略：读 [references/common-patterns.md](references/common-patterns.md)
- 格式归一化：读 [references/format-normalization.md](references/format-normalization.md)
- Excel 提取：读 [references/excel-extraction.md](references/excel-extraction.md)
- Word 提取：读 [references/word-extraction.md](references/word-extraction.md)
- PDF / PPT 提取：读 [references/pdf-ppt-extraction.md](references/pdf-ppt-extraction.md)
- 输出与质量门：读 [references/output-and-validation.md](references/output-and-validation.md)
