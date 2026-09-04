# Chable 後端安全評估報告（實測證據）

**評估對象**: `us-east1-chable-91c06.cloudfunctions.net`（mgobill 的 Chable: Business Empire 正式後端）
**評估日期**: 2026-08-12（Day-1 授權補測：2026-08-13，LoA-CHABLE-2026-001）
**方法**: 以 Firebase Auth REST 註冊測試帳號取得 idToken，直接 HTTP 呼叫 Cloud Functions（**非破壞性探測**：僅用不存在的假 ID、不操作他人真實資料）

> **授權狀態**: 2026-08-13 取得 LoA-CHABLE-2026-001（生效 20260813–20260820）。
> 授權後新建測試帳號一律使用 `test_pentest_XX@chable.test` 慣例；Day-1 補測（marketplace 播種、
> 買店價格信任、跨帳號擁有權）結果見 `bot/reports/loa-day1-*.md`。

---

## 1. 摘要

| 面向 | 結論 |
|---|---|
| Admin gate | ✅ **硬防護**：4 支 admin 函式一律 403，client 帶 `isAdmin`/`admin`/`adminKey` 旗標無效，檢查在伺服器端 |
| 存在性驗證 | ✅ 有：假 ID 全部正確回 `not found` 類錯誤 |
| 獎勵 rate limit | ✅ 有冷卻：廣告獎勵連打 3 次只發 1 次 |
| App Check | ⚠️ 三面：Firestore client 端鎖死；**Auth signUp/signIn 已開 enforcement（2026-08-14,401 實測）**；functions 仍未套用（既有帳號可用 refresh 續命 + 純 idToken 呼叫整個後端） |
| 註冊 | ✅ **已修復（2026-08-14）**：Auth App Check enforcement 生效，signUp 一律 401（08-13 前實測 1.9 accounts/s 為歷史數據） |
| 擁有權驗證 | ❓ **未驗證**（需跨帳號真實資料，未授權不測） |
| 購買價格信任 | ❓ 未驗證（參數名與推測不符，無法進入購買邏輯） |

## 2. 測試範圍與方法

- **測試帳號**：`probe_1786543790_buff@example.com`（UID `NTn3fNz9XtUtdX2QNkrWS7v3QbG2`）、`probe2_*`（UID `kX51eEMAISVUqXRVPF7dPDNv4iT2`）
- **呼叫方式**：`POST https://us-east1-chable-91c06.cloudfunctions.net/<fn>` + `Authorization: Bearer <idToken>` + `{"data": {...}}`
- **Token 取得**：`POST https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyARnsZGZA4bgCLdrifLnmI3DS_t_UW6jGQ`（APK 內嵌的公開 API key）
- **原則**：只用假 ID / 空 payload / 自己的測試帳號；不做任何跨帳號操作。

## 3. 各項驗證細節

### 3.1 認證層

| 測試 | 結果 | 證據 |
|---|---|---|
| 未帶 token 呼叫 | 401 | 首次 us-east1 探測（無 Authorization header）回 401 |
| 帶 token 呼叫 | 200/400/403 | 帶 idToken 後全部正常回應 |
| 註冊開放性 | 開放(08-13)→ 🔒 已封(08-14) | 08-13:兩帳皆成功建立;08-14:signUp 一律 401 `Firebase App Check token is invalid.`(probe30) |

### 3.2 App Check 狀態

> **2026-08-14 更新**:開發者已開啟 **Firebase Auth 的 App Check enforcement**。
> 完整邊界矩陣(signUp/signIn/refresh/Firestore REST/Functions × 無 header/garbage/JWT 假 token)
> 見 `bot/reports/appcheck-enforcement-2026-08-14.md`(probe30,2026-08-14 06:56 UTC 實測)。

| 面 | 狀態 | 實測證據 |
|---|---|---|
| **Auth signUp / signIn** | 🔒 **已強制執行(2026-08-14 起)** | 無 header / garbage / JWT 形狀假 token 一律 401 `Firebase App Check token is invalid.`(status UNAUTHENTICATED) |
| **Auth refresh token**(`identitytoolkit /token`、`securetoken /token`) | 🔓 豁免(Firebase 設計:enforcement 涵蓋 sign-in/sign-up,token 交換端點不檢查) | 三變體皆 200,正常發放新 idToken |
| **Firestore**(client 直連 / REST) | 🔒 **有強制執行**(規則層) | 08-12 logcat:`Integrity API error (-14)` → 佔位 token → 所有查詢 `PERMISSION_DENIED`;08-14 REST 重驗:讀/寫/無 auth 皆 403 `Missing or insufficient permissions.` |
| **Cloud Functions** | 🔓 **未強制執行** | 帶純 Auth token(無 App Check header)即可 200 成功,且寫入真實資料;帶 garbage App Check header 也 200(08-14 重驗) |

**殘餘風險**:refresh 豁免 + functions 未 enforcement = 08-14 之前建立的既有帳號可無限續命並持續自動化整套免費面(簽到/獎勵/執照/推薦)。新帳號灌水已斷根。

### 3.3 Admin gate（4 支函式）

全部回相同錯誤，且**不受 client 旗標影響**：

```
POST adminSeedStoreToUserV1       {"data":{"isAdmin":true,"userId":"zz","storeId":"zz"}}
POST adminSeedStoreToUserV1       {"data":{"admin":true,"userId":"zz","storeId":"zz"}}
POST adminSeedStoreToUserV1       {"data":{"adminKey":"zz-secret","userId":"zz","storeId":"zz"}}
→ 403 {"error":{"message":"Only admin users can run this action.","status":"PERMISSION_DENIED"}}
```

`adminStartImpersonationV1`、`adminRunTakeoverDebugCycleV1`、`adminRegenerateRankingsDebugV1` 同（帶 `isAdmin:true` 仍 403）。
**結論**：admin 判定基於伺服器端資訊（custom claims 或 admin SDK 查表），非 client 可偽造。

### 3.4 存在性驗證

| 函式 | 請求（假 ID） | 回應 |
|---|---|---|
| `surrenderTakeoverV1` | `{"takeoverId":"zz-nonexistent-takeover"}` | `Takeover not found.` (FAILED_PRECONDITION) |
| `sellStoreV1` | `{"storeId":"zz-nonexistent-store"}` | `Store not found.` (NOT_FOUND) |
| `configureInitialMaintenanceV1` | `{"storeId":"zz-nonexistent-store"}` | `Store could not be found.` (FAILED_PRECONDITION) |
| `syncBrandNameToGlobalV1` | `{"storeId":"zz-nonexistent-store"}` | `Store not found.` (NOT_FOUND) |

**結論**：操作前先驗證目標存在，具備基本資料完整性檢查。

### 3.5 獎勵 rate limit（grantActionChargeRewardV1）

```
第 1 次 → {"granted":1,"availableScans":3,"configuredRewardAmount":5,...}
第 2~4 次（連打）→ {"granted":0,"availableScans":3,...}   （lastReplenishTime 不變）
```

**結論**：直接呼叫即發獎勵（無廣告驗證），但有伺服器端冷卻。冷卻窗口長度未測。

### 3.6 參數驗證（400 系列，參數名與推測不符）

| 函式 | 送出的參數 | 回應 |
|---|---|---|
| `purchaseStoreV1` | `{storeId, purchasePrice}` | `Missing required purchase fields.` |
| `renameBusinessChainV1` | `{businessKey,chainName}` / `{chainKey,chainName}` / `{businessKey,newName}` | `Business key and new chain name are required.` |
| `applyReferralCodeV1` | `{referralCode:"99FC74A1E6"}`（真實 10 碼格式） | `Referral code is required.` |

**結論**：這三支的實際參數名與推測不同，無法進入業務邏輯，故**無法評估價格信任 / 推薦碼濫用**。

### 3.7 功能正常（200）

| 函式 | 回應重點 |
|---|---|
| `processAttendanceStartupV1` | 完整簽到資料；`cashBalance: 3000000`（**兩帳號一致 → 預設起始資金**，非個別獎勵；APK 內亦有 `startingCash`/`$3,000,000` 字串佐證） |
| `ensureReferralCodeV1` | `{"referralCode":"99FC74A1E6"}` |
| `ensurePublicCompanyProfileV1` | `companyId`、`hadSnapshot` |
| `purchaseOperatingLicenseV1` | `purchased:true`、`price:10000`、`operatingLicensesOwned:11`、扣款後 `cashBalance` |
| `grantActionChargeRewardV1` | `granted`、`availableScans`、`configuredRewardAmount:5` |

## 4. 未驗證項目（決定「防護是否到位」的關鍵）

| 項目 | 為何未測 | 若驗證缺失的影響 |
|---|---|---|
| **擁有權驗證**（sellStore / surrenderTakeover / rename / syncBrandName / configureMaintenance） | 需 A 帳號持有真實商店、B 帳號嘗試操作 → 屬實際攻擊他人資料，**需開發者授權** | 可賣他人商店、投降他人攻佔、覆寫全域商店名（griefing / 經濟破壞） |
| **purchaseStoreV1 價格信任** | 參數名未知 | 若價格由 client 提供且未比對 → 任意低價買店 |
| ~~**applyReferralCodeV1 洗碼**~~ | ~~參數名未知~~ | ~~洗帳號刷推薦獎勵~~ |
| **applyReferralCodeV1 洗碼** ✅ 已實證（2026-08-12 下午） | 參數 = **`referrerCode`**，已破解 | **有界**：碼主每次 +1 bonus 行動點數，**每碼上限 2**（第 3 個 sock 回 `applied_cap_reached`）；一帳只能套 1 碼。實測：3 sock → 主帳號 3→5 點後停止。**對公平性影響：無** |
| **grantActionChargeRewardV1 冷卻窗口** | 需長時間觀察 | 若窗口很短 → 廣告獎勵可被刷 |

## 5. 風險評估結論

```
已驗證的防護水準：良好（admin gate 硬、存在性驗證有、獎勵有限流、掃描鏈有 App Check、
            Auth signUp/signIn 已開 App Check enforcement(2026-08-14)、推薦有界、
            冷卻/行動點數有交易保護、閒置有自動清算）
未達成/未測：擁有權 / 價格信任（需先有店，無法從 API 取得商店 → 未達）
已修復：① 註冊濫用（App Check enforcement 已擋 signUp/signIn,2026-08-14 實測 401）
建議強化（非漏洞）：② functions 套 App Check enforcement(現在的最優先項——
            既有帳號可 refresh 續命 + 純 idToken 呼叫,自動化未根除)
            ③ refresh 豁免為 Firebase 設計,殘餘自動化需靠帳號治理補
```

> 詳細實證與商店家族驗證表見 `bot/FINDINGS.md`（以該文件為準）。

## 5.5 bot 階段新發現（2026-08-12 下午）

- **`queueGameplayActionV1` 完整破解**：`actionType`（`in_person_visit`/`maintenance_change`/`regional_visit`/`defense_email`/`defense_physical`/`email_management`）+ `storeId`，可排入遊戲動作佇列。
- **`consumeActionChargeV1` / `getOperatingLicenseQuoteV1` / `verifyAppVersionV1` / `resolveLocationScoresV1` 確認存在**。
- **買執照消耗行動點數**、**廣告獎勵有冷卻**（點數滿時 `granted:0`）。
- **自動化證明**：`chable/bot/` 用純 HTTP 註冊帳號並完成簽到/獎勵/買執照/推薦鏈全流程，輸出成長報告。新帳號 3,000,000 起始現金 + 10 張免費執照。

## 5.6 最終結論（2026-08-12，專業版）

**經濟鏈全貌**：GPS → Overpass 掃描（client）→ Firestore `nearby_scan_cache`（App Check 保護）→ marketplace listings → `purchaseStoreV1` → 維護/賣店/攻佔。

**總體判定：後端經濟防護水準良好，未發現可影響公平性或經濟的漏洞。**

| 面 | 判定 |
|---|---|
| 買店 / 維護 / 賣店 / 品牌 / 攻佔 / 實體票券 | ✅ 封閉：需真實 storeId，storeId 只能來自買店，買店需要掃描快取（Firestore REST 讀寫皆 403 實測） |
| 推薦 | ✅ 有界（一帳一碼、自套拒絕、每碼 bonus 上限 2） |
| 冷卻 / 行動點數 | ✅ 有交易保護（平行呼叫無競態繞過） |
| 閒置帳號 | ✅ 有 `auto_liquidation` / streak 遷移 / 經濟過期機制 |
| 註冊無 rate limit | ✅ **已修復（2026-08-14）**：Auth App Check enforcement 擋下 signUp/signIn（401 實測） |
| functions 未套 App Check | 🔴 **仍是唯一未上鎖的後端面**（2026-08-14 重驗：純 idToken 200）＋ refresh 豁免 → 既有帳號自動化持續存在 |
| App Check 鎖定模擬器/root | ⚪ 產品決策，非漏洞（over-blocking 是安全的失敗方向） |

**建議優先序（2026-08-14 更新）**：① ~~註冊 rate limit~~ ✅ 已由 Auth App Check enforcement 達成；② functions 套 App Check enforcement（現在的最優先項，與 Firestore/Auth 一致）；③ 既有帳號自動化靠帳號治理（閒置清算/異常偵測）補（refresh 豁免為 Firebase 設計）；④ 觀察模擬器/root 流失與支援量（產品面，登入現在也被擋）。
**誠實標註**：買店價格信任與跨帳號擁有權為未達成/未測項目，非實證，不得引用。
**唯一待驗**：marketplace 是否全域每日播種（20260813 遊戲日 rollover 測試）。

## 6. 附錄

- **相關檔案**：`ChableApp-cloud-functions.md`（API 清單與風險表）、`ChableApp-firebase-analysis.md`（Firebase 設定）、`Chable-流程紀錄.md`（時間線）
- **測試帳號資料**：見 `Chable-流程紀錄.md`
- **建議後續**：若獲得 mgobill 授權，補測「跨帳號擁有權驗證」與「purchaseStoreV1 參數結構」即可完成完整評估；或將本報告整理為負責任揭露信。
