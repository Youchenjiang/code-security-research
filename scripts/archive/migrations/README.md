# 歷史遷移腳本存檔 (Migration History Archive)

本目錄下的 `history/` 子資料夾封存了專案在重組知識庫、論文去重、下劃線轉空格、格式校準過程中產生的 26 個歷史一次性腳本。

---

## ⚡ 核心能力已全面整併

為避免歷史腳本中「寫死特定檔名」帶來的維護困擾，所有實用功能（包含健康檢查、雙向對齊、檔名清洗、重複排除）已全面升級重構為頂層的通用命令行工具：

👉 **[scripts/paper_cli.py](file:///c:/Users/g1014/Documents/GitHub/Youchen/code-security-research/scripts/paper_cli.py)**

未來進行文獻管理時，請直接使用統一指令：
```bash
# 全庫健康檢查 (100% 鏈結、雙鏈、YAML、檔名)
python scripts/paper_cli.py audit

# 雙向鏈結自動掛載與同步
python scripts/paper_cli.py sync

# 檔名規範化洗滌器
python scripts/paper_cli.py normalize

# 跨分類筆記查重與孤兒檔案清理
python scripts/paper_cli.py dedup
```
