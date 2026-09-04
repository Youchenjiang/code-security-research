# Chable APK — Cloud Functions 呼叫端點（已實測確認）

**分析對象**: `chable/ChableApp/com.mgobill.chable.apk`（v2.2.8 / code 145）
**分析日期**: 2026-08-12
**驗證方式**: 以 Firebase Auth REST 註冊測試帳號取得 idToken，直接 HTTP 呼叫各候選端點，比對 200/400/403/404 回應。

---

## 關鍵結論

1. **Cloud Functions 部署在 `us-east1` region**（不是 SDK 預設的 us-central1；`https://us-central1-...cloudfunctions.net/*` 全部 404）。
2. **Functions 沒有開啟 App Check enforcement**——只要帶 Firebase Auth idToken 就能呼叫，**不需要 App Check token**。
3. 對比之下 **Firestore client 端被 App Check 鎖死**（`PERMISSION_DENIED`，已實證）；但 functions 用 admin SDK，不受影響。
4. 註冊帳號即可取得 token：email/password 註冊在該專案是**開放**的（API key 為 APK 內嵌的公開值）。

## 呼叫方式

```
POST https://us-east1-chable-91c06.cloudfunctions.net/<functionName>
Header: Authorization: Bearer <Firebase idToken>
Body:   {"data": { ...參數... }}
```

取得 token（Firebase Auth REST，公開 API key）：
```
POST https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyARnsZGZA4bgCLdrifLnmI3DS_t_UW6jGQ
Body: {"email":"...","password":"...","returnSecureToken":true}
```

---

## 可呼叫函式（12 支，皆已實測）

| 函式 | 實測結果 | 已知參數 / 回應 |
|---|---|---|
| `processAttendanceStartupV1` | ✅ 200 | 無參數。回傳 `gameDayKey`、`attendanceStreakDays`、`attendanceTotalDaysPlayed`、`attendanceStreakStepAmount`、`cashBalance` 等 |
| `ensureReferralCodeV1` | ✅ 200 | 無參數。回傳 `referralCode`（例 `99FC74A1E6`） |
| `ensurePublicCompanyProfileV1` | ✅ 200 | 無參數。回傳 `companyId`、`hadSnapshot`、`forceRecompute` |
| `grantActionChargeRewardV1` | ✅ 200 | 無參數。回傳 `granted`、`availableScans`、`lastReplenishTime` |
| `purchaseOperatingLicenseV1` | ✅ 200 | 需 businessKey（未帶時用預設）。回傳 `purchased`、`price`、`operatingLicensesOwned`、`cashBalance` |
| `purchaseStoreV1` | ⚠️ 400 | 錯誤訊息：`Missing required purchase fields.` |
| `sellStoreV1` | ⚠️ 400 | 需要 `storeId`（錯誤訊息：`Store ID is required.`） |
| `surrenderTakeoverV1` | ⚠️ 400 | 需要 `takeoverId`（`Takeover ID is required.`） |
| `renameBusinessChainV1` | ⚠️ 400 | 需要 `businessKey` + 新連鎖名（`Business key and new chain name are required.`） |
| `applyReferralCodeV1` | ⚠️ 400 | 需要 `referralCode`（`Referral code is required.`） |
| `configureInitialMaintenanceV1` | ⚠️ 400 | 需要 `storeId`（`Store ID is required.`） |
| `syncBrandNameToGlobalV1` | ⚠️ 400 | 需要 `storeId`（`Store ID is required.`） |

## 管理員限定（403：`Only admin users can run this action.`）

| 函式 | 用途（推測） |
|---|---|
| `adminSeedStoreToUserV1` | 塞商店給玩家 |
| `adminStartImpersonationV1` | 化身玩家 |
| `adminRunTakeoverDebugCycleV1` | 攻佔除錯循環 |
| `adminRegenerateRankingsDebugV1` | 重建排行榜 |

## 不存在（404，已測試排除）

`processAttendanceStartup`、`attendanceStartup`、`ensureReferralCode`、`purchaseStore`、`getProfile`、`createAccount`、`startGameDay(V1)`、`scanNearby(V1)`、`selectDailyCategories`、`computeDailyRankings`、`queueHostileTakeoverStart`、`startImpersonation`、`grantScanChargeReward`、`scanNearbyAt`、`updateQueuedBusiness`、所有 `set*` 設定函式、`leaderboard`、`getRankings`

## 風險評估（2026-08-12 非破壞性探測）

| 等級 | 函式 | 說明 |
|---|---|---|
| 🔴 高影響/低風險 | 4 支 `admin*` | 403 `Only admin users can run this action.`，有伺服器端防護，但若被繞過影響最大 |
| 🟠 中高（驗證未知） | `purchaseStoreV1` `sellStoreV1` `surrenderTakeoverV1` `syncBrandNameToGlobalV1` `configureInitialMaintenanceV1` `renameBusinessChainV1` | 已確認有存在性驗證（`not found`），擁有權驗證未測（需跨帳號，未授權不測） |
| 🟡 中 | `applyReferralCodeV1` | 推薦碼洗帳號風險 |
| 🟢 低 | `grantActionChargeRewardV1` | 直接呼叫即發獎（`granted:1`，`configuredRewardAmount:5`），無廣告驗證，但有 rate limit（連打 3 次皆 `granted:0`） |
| ⚪ 低 | `processAttendanceStartupV1` `ensureReferralCodeV1` `ensurePublicCompanyProfileV1` | 設計為自由呼叫，靠 game-day key 限流 |

**說明（非漏洞）**：functions 未開 App Check enforcement + 註冊開放 → 免費面（簽到/獎勵/執照/推薦）可被純 HTTP 自動化；**全部有界且不影響公平性**（核心經濟鏈被掃描快取的 App Check 保護，見商店家族驗證）。建議作為防禦縱深套用 App Check + 註冊 rate limit。

**已知限制**：`renameBusinessChainV1`/`applyReferralCodeV1`/`purchaseStoreV1` 的參數名與推測不符（送合理參數仍回 `required`），無法進一步判斷價格信任問題。

## 附註

- **這些呼叫會寫入開發者的正式環境（production Firestore）**：實測帳號已獲得 300 萬起始現金、經營執照、簽到資料等。測試請使用一次性帳號。
- idToken 有效期約 1 小時，可用 refreshToken 換新。
- 未帶 token 呼叫 → 401（函式需要驗證）。
- 資料層（Firestore）直接讀取仍被 App Check 擋住，但可透過上述函式間接操作。

---

## 更新（2026-08-12 下午，bot 階段補測）

### 新確認存在（原 404 清單之外）

| 函式 | 實測 | 參數（已破解） |
|---|---|---|
| `applyReferralCodeV1` | ✅ 200 | **`referrerCode`**（不是 referralCode）。`{referrerCode:"<10碼>"}` → `{status, applied, rewardGranted, bonusAfter, referralBonusCap}`；碼主 +1 bonus 行動點數，每碼上限 2（第 3 個 sock → `applied_cap_reached`） |
| `queueGameplayActionV1` | ✅ 400→200 路徑 | **`actionType`**（snake_case）。有效值 **9 個(2026-08-14 probe37 全枚舉)**:`in_person_visit`/`maintenance_change`/`regional_visit`/`defense_email`/`defense_physical`/`email_management`(需 `storeId`)、`takeover_physical`(需 **`takeoverId`**)、`takeover_start`(需 **`targetLocationFingerprint`** H3,純遠端攻佔入口)、`surrenderTakeoverV1` 獨立函式(需 `takeoverId`)。⚠️ 舊記錄「6 種皆需 storeId」不正確:`takeover_physical`/`takeover_start` 不走 storeId |
| `getOperatingLicenseQuoteV1` | ✅ 200 | 無。回報價 `{price, basePrice, operatingLicensesOwned, totalLicenseNumber, paidLicenseNumber, pricingConfig{freeIndustryLicenseCount:10, licenseQuadraticBase:10000}}` |
| `consumeActionChargeV1` | ✅ 200 | 無。消耗 1 行動點數 `{consumed, availableScans, lastReplenishTime, actionChargeCost}` |
| `verifyAppVersionV1` | ✅ 200 | 無。`{isApproved, minVersion, serverTime}` |
| `resolveMarketplaceListingPricesV1` | ✅ 200 | 位置參數（lat/lon/locationFingerprint H3/locationNumber）；今日回 `{listings: [], gameDayKey}`（marketplace 未播種，無法進一步測） |
| `resolveLocationScoresV1` | ✅ 200 | 無。`{results: []}` |

### 機制補充（實測）

- **買執照消耗行動點數**：`purchaseOperatingLicenseV1` 每張扣 1 點，不足時 `Not enough action charges.`。
- **廣告獎勵冷卻**：`grantActionChargeRewardV1` 點數滿時 `granted:0`；消耗後才能再領。
- **推薦 bonus 超過上限**：3 base + 2 referral = 5 availableScans。
- **執照價格**：二次方，paid #n = 10000×n²（10k/40k/90k/160k/250k/360k/490k/640k…）。

### 仍卡關

- **`purchaseStoreV1`**：kitchen-sink（50+ 候選鍵）、正數價格、巢狀物件、12,108 鍵超巨型 payload、真實 H3 指紋、真實 OSM 掃描資料（20+ 形狀）皆 `Missing required purchase fields.`；根因 = 伺服器讀取掃描快取（App Check 保護，Firestore REST 403）。需等 marketplace 有 listings 時用真實 listing 物件比對（`probe-marketplace.js` 已就位，20260813 測試）。
- **`issuePhysicalActionTicketV1`**：已破解座標鍵 = **`requesterLatitude`/`requesterLongitude`**；有效實體類型只有 `in_person_visit` / `defense_physical`，**皆需 storeId**（`Store ID is required for this action.`）→ 無店即死胡同。

### 商店家族全驗證（2026-08-12 深夜）

買/維護/賣/品牌/攻佔/實體票券全部需要真實 storeId/takeoverId,而 storeId 只能來自買店 → 買店需要掃描快取(App Check 擋死)→ **整組封閉**:

| 函式 | 結果 |
|---|---|
| `purchaseStoreV1` | `Missing required purchase fields.` |
| `configureInitialMaintenanceV1` | `Store could not be found.` |
| `syncBrandNameToGlobalV1` / `sellStoreV1` | `Store not found.` |
| `surrenderTakeoverV1` | `Takeover not found.` |
| `queueGameplayActionV1`(6 種) | `Store not found.` |
| `issuePhysicalActionTicketV1` | `Store ID is required for this action.` |

**掃描鏈**:GPS → Overpass(client)→ Firestore `nearby_scan_cache`(App Check)→ marketplace → purchase。Firestore REST 讀/寫皆 403。

### 自動化 bot

`chable/bot/`（`bot.js`）：`register` / `run` / `daemon` / `status`，輸出 `reports/*.md`。
示範帳號 `chable_demo_1786545730@example.com`：18 張執照、淨資產 3,000,000、3 個推薦套用。
