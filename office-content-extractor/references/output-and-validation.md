# 输出与验证

## 目录

- 输出格式选择
- chunk 规则
- 最小元数据
- 验证样本

## 输出格式选择

常见输出只有三类：

- 纯文本
- Markdown
- chunks

建议：

- 只做全文检索时，纯文本或紧凑 chunks 即可
- 需要人工读和复核时，优先 Markdown
- 需要下游检索或问答时，优先 chunks

## chunk 规则

chunk 应满足：

- 顺序稳定
- 大小可控
- 尽量不跨自然边界

自然边界示例：

- Word 的段落或表格
- Excel 的 sheet 或多行片段
- PDF 的页
- PPT 的 slide

## 最小元数据

即使是通用提取，也建议保留：

- `source_format`
- `output_format`
- `parser_strategy`
- `chunk_index`
- `page_number` / `sheet_name` / `slide_number`

## 验证样本

至少验证这几类样本：

- 标准文件
- 空内容文件
- 大文件
- 扫描件 PDF
- 含复杂表格的 Word/Excel
- 含图片的 PPT

验证时重点看：

1. 有没有丢内容
2. 顺序是否正确
3. 输出是否过碎或过长
4. 失败时能否定位原因
