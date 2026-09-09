# 📄 高精度 PDF 轉 Markdown 解析模組 (Parser)

本目錄提供基於 Node.js 與 `pdfjs-dist` 的論文排版解析工具，具備佈局感知、表格重構與圖片抽取能力。

## 核心工具

- **`pdf-to-md.js`**: 通用 PDF 轉 Markdown 解析引擎。

### 功能特點
1. **佈局感知提取**：保留雙欄排版之閱讀順序。
2. **啟發式表格偵測**：自動將論文中的對比表格重構為標準 Markdown 表格語法（`| col1 | col2 |`）。
3. **內嵌圖片抽取**：自動解碼並提取論文中的圖表與架構圖，保存為 PNG 並插入 Markdown 連結。
4. **YAML 元數據生成**：自動提取 PDF 屬性生成 Frontmatter。

### 使用方式
```bash
# 解析單一 PDF 檔案
node scripts/parser/pdf-to-md.js --input "path/to/paper.pdf" --output "path/to/output.md"

# 批次解析目錄中的所有 PDF
node scripts/parser/pdf-to-md.js --dir "raw-papers/2026"
```
