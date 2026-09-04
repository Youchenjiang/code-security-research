# 後端 API 續測計畫(2026-08-16)

> 前提:19 支公開函式 + 7 支 admin 已全數呼叫過,測試紀錄見 `覆蓋率盤點.md` §2。
> 這份計畫只涵蓋「**還沒做完**」的部分,分三類:純 API 可立即執行 / 需裝置(封閉) / 需委託人確認。
> 現有工具:認證在 `bot/api.js`、雲函式清單 `bot/bot.js`、規格文件 `bot/*-規格.md`、逆向產出 `_tools/blutter_out/`。

---

## 1. 純 API 續測(不需要裝置,可立即執行)

### 1.1 takeover_start 格式確認 ✅ + isOwned 語意更正(probe46 + 後續,2026-08-16)

**確認項(probe46,`reports/probe46-isowned-takeover-2026-08-16.log`)**:takeover_start 的正確
fingerprint 格式 = **`osm_node_<id>`**(與 resolve locationFingerprint 相同,exact match),**不是 H3
cell**——probe37/38 全 not found 是格式錯誤假陰性。

**⚠️ 語意更正(用戶指正,probe47–49 補充)**:isOwned = 全域「該 fingerprint 在伺服器端 store
記錄中存在」旗標(02/03 同查同結果,probe45/49),不等於「本帳號擁有」。**但 probe49 實證測試環境
確實有第三方店**:022(7-Eleven)與松崗(YouBike)對 03/02 皆非 `already own` → 都是非測試帳號的
store 記錄且不 protected(有效 target),「測試環境沒有他玩家的店」的說法**已更正為錯誤**。probe48:
松崗不在本帳號 08-15 scan cache(被 app 掃描類型過濾,與 i郵箱同型)→ 正常玩家同款 app 掃不到 →
松崗較可能為開發者/admin 種子;022 是正常商業類且在 cache → 較可能為正常玩家(或開發者測試)購買;
owner 身份 API 端無法 100% 區分(需 Firestore `stores` 或委託人說明)。

**閘門鏈(probe49 實測完整解出)**:`Target store not found.`(指紋不在索引)→ `You already own
this store.`(呼叫者擁有)→ `Target store ... is protected.`(034 有購買保護期;022/松崗無 → 較老,
可能為保護期過或無防護狀態)→ `Insufficient cash for escrow.`(escrow 現金不足,02 帳號)→
`Physical action ticket is required.`(有現金、需票券,03 帳號)→ 實體行動票券。`Physical action
ticket is required.` 之後的鏈:

```
issuePhysicalActionTicketV1        # 0x625a38,payload = {actionType, requesterLatitude/Longitude,
  → {ticketId}                     #   targetLatitude/Longitude, 條件鍵(storeId/takeoverId/
                                   #   targetLocationFingerprint/targetOwnerUserId/industryId)}
queueGameplayActionV1              # 0x621f28,payload = {actionType, storeId, locationFingerprint,
  takeover_start + ticketId        #   industryId, targetLatitude/Longitude, actionChargeCost(client 自報!),
                                   #   physicalActionTicketId, payload}
```

**2026-08-16 probe50/51:完整列舉(無截斷)——第三方店不是 2 間,是 10 間**。probe46/47 的
`out center 150/300` 截斷掃描漏店(probe47 連 85m 外的 034 都漏)。probe50 改 per-category union
(`out center 10000`)完整列舉 + resolve:5km 854 元素 → isOwned:true 4 間(034 測試帳號 + 松崗 +
022 + **新厝加油站高鳳站洗車** `osm_way_793888665` car_wash @0.40km base=1,960,000,全測試帳號非
already-own → 第三方;4 間全在 0–0.5km);5–10km 4163 元素 → **7 間第三方**(懶人時光 cafe、鎮北國小
YouBike、全聯福利中心、美廉社(鳳山)、牛潮埔公園 YouBike、高雄大順郵局、肯德基,全在 7.3–9.1km
鳳山/三民/苓雅弧帶;probe51 per-account 全數非測試帳號)。→ **10km 內 11 間 isOwned:true = 1 測試
+ 10 第三方**;3 間 YouBike(松崗/鎮北國小/牛潮埔公園)同型同價帶且被 app 掃描過濾 → 較可能開發者/
admin 種子;其餘 7 間正常商業類玩家或種子皆有可能。probe48 的「松崗是 10km 內唯一非測試帳號 store
記錄」結論**已作廢**。產物:`bot/probe50.js`、`bot/probe51.js`、`reports/probe50-enum-5km-full-2026-08-16.log`、
`reports/probe51-ring-ownership-2026-08-16.log`。

**client 端距離檢查存在**(0x625cec,門檻 1.5×radius+0.05km,僅 takeover_start)→ 伺服器端是否也
驗證距離、票券可否被任何登入者取得、`actionChargeCost` 是否被覆寫,皆未測。**發票/攻佔屬真實
狀態變更,需委託人授權(§3.2)後才可測 probe47。**

**2026-08-17 probe52/53(純 API 追加,無需委託人)**:

- **保護期分類**:10/10 第三方店**全部不在購買保護期**(5 測試帳號對每間店的 takeover_start 無一回
  `protected`);只有測試帳號 034(08-15 購入)在保護期 → **沒有一間第三方店是近期被買走的**。
- **08-15 真機掃描列表重建(cache 成員列舉)= 95 間**:第三方店中只有 **022** 在列表內(被顯示但
  當時誤判為本帳號店);松崗/新厝洗車在 2km 內但被 app 掃描管線排除;環帶 7 間在 2km 外。
- **掃描濾網實證**:YouBike 34/34、公園 22/22、加油站 3/3、洗車/幼稚園/圖書館/夜市/消防站等
  全數被 app 排除(規則在伺服器端,APK 無類別字串)→ 松崗/鎮北/牛潮埔/新厝洗車 = 正常玩家
  **掃不到買不到**的 4 間第三方店 → 幾乎確定為種子/admin 建立。
- **owner 身份確認已依用戶指示擱置**(需委託人確認或 root 裝置,不主動推進)。

---

### 1.2 moderator 判定方式逆向

**背景**:`買店滲透盤點.md` 記錄 admin 角色外另有 `Moderator or admin access is required.`(moderator 與 admin 權限分離)→ 若兩者檢查點不同,可能存在權限設定缺陷。

**方法**:
1. 在 blutter 產出(`_tools/blutter_out/asm/`)搜 `Moderator or admin access is required.` 的引用函式,找出判定邏輯(讀哪個 Firestore 欄位?`users/{uid}` 的 role?)。
2. 若判定欄位在 `users/{uid}`(App Check 403 牆後)→ 純 API 不可達,記錄為封閉。
3. 若判定有 client 自報成分(如 header/參數)→ 實測。

**判定標準**:找出檢查函式與資料來源,判定「封閉」或「可測」。預期多數是封閉(Firestore 牆),此項是收尾性質。

---

### 1.3 rename 驗價前置:businessKey 關聯(A7 假說)

**背景**:`renameBusinessChainV1` 已破解參數(`{businessKey, newCustomBrandName}`,probe36),但驗價(成本 client 自報)需真實 businessKey,而 businessKey 來源是 `_businessKeyForIndustryId`(A7 假說,未驗證)。

**方法**:逆向 `_businessKeyForIndustryId`,確認 businessKey 是否可由**已知可得的 industryId**(掃描回應/經濟資料)推導。若可 → businessKey 即可得,rename 驗價的純 API 路打開。

**判定標準**:A7 假說成立 → 設計 probe47 實測 rename 成本(篡改 cashCost 看是否被伺服器覆寫);不成立 → 封閉。

---

### 1.4 (備援)takeover_start 的 server 端 fingerprint 計算

僅在 1.1 判定「格式歧義是主因」時啟動:逆向 app 端 `takeover_start` 呼叫點(`queueGameplayActionV1` 參數建構處),還原 targetLocationFingerprint 的真實產生方式(是 `_nearbyScanTileKey` 還是 OSM typed id),再回頭重測。

---

## 2. 需裝置/憑證(目前封閉,記錄解鎖條件)

| 項目 | 卡點 | 解鎖條件 |
|---|---|---|
| P1 價格信任(purchaseStoreV1 篡改價) | `officialBusinessId` 真值三路全封(resolve 無 ob / Firestore 403 / 爆破不可行) | root/debug 裝置抓真實請求,或 App Check token 重放 |
| 跨帳號擁有權(IDOR) | 需真實 storeId | 同上 |
| rename 驗價 | 需真實 businessKey(若 1.3 失敗) | 同上 |
| 全圖掃描權 | scan cache 寫入被 App Check 擋 | App Check token 重放(MITM 能力) |
| admin@chable.app 密碼攻擊 | 需確認 LoA 範圍 | 委託人書面授權 |

> 真機測試路已由委託方於 2026-08-15 終止;以上僅保留為「若裝置路重開」的執行清單,不主動推進。

---

## 3. 需委託人確認

1. **admin 密碼攻擊**是否在 LoA 範圍內(硬編碼 admin@chable.app,`ChableApp-firebase-analysis.md` 有紀錄)。
2. **遠端攻佔鏈推進授權(2026-08-16 新増,緊急)**:probe46 已證實 takeover_start 對全域已購店是
   **有效 target**(松崗停車場 `osm_node_8882051701`)。下一閘門是實體票券——若發票(probe47)成功,
   等於「任何登入者可對任何已購店發起真實攻佔」的證據鏈成形。是否:
   a. 只測到「發票成功/失敗」為止(推薦,證據已足夠,不碰真實狀態變更);
   b. 繼續測到「takeover_start 帶票執行」(會真實改寫松崗停車場的擁有權狀態,需明確授權)。
   預設為 (a),發票測試本身也建議先確認。
3. 掃描範圍上限:isOwned oracle 掃描(1.1)的商家數量是否有上限(建議單次 <200 間,分區進行)。

---

## 4. 執行順序與產物

| 步驟 | 動作 | 產物 |
|---|---|---|
| 1 ✅ | 1.1 isOwned oracle + takeover_start(probe46)——**完成,突破** | probe46.js + log + FINDINGS §6.4 + 本計畫 §1.1 更新 |
| 1.5 ✅ | probe47–49(唯讀追加,用戶質疑「松崗是否真有人佔領」):松崗 OSM 真相 + 5km 密度(47)、cache 成員測試 + 5–10km 環帶(48)、per-account 擁有權 + 閘門鏈(49)——**完成;022/松崗 證實為第三方店** | probe47/48/49.js + logs + FINDINGS §6.4 + 總整理/買店滲透盤點 §5.7 更新 |
| 1.6 ✅ | probe52/53(唯讀追加):保護期分類(10/10 第三方店無保護)+ 08-15 掃描列表重建(95 間)+ 掃描濾網確認(YouBike/公園/洗車等系統性排除)——**完成** | probe52/53.js + logs + FINDINGS §6.4 更正 4 |
| 2 ⏸️ | 1.1b 票券閘門:需委託人授權(§3.2)——**注意 target 是 022/松崗(真實第三方店),執行攻佔=改寫真實玩家/開發者店,務必先授權** | 待定 |
| 3 | 1.3 businessKey 關聯逆向(純逆向,不需授權) | 規格文件更新 |
| 4 | 1.2 moderator 逆向(純逆向) | 規格文件更新 |
| 5 | 全部結束後更新總整理 + 覆蓋率盤點 | 文件同步 |

**判定口訣**:能純 API 做的先做(1.1 已突破、1.3/1.2 是純逆向),會改寫真實狀態的(1.1b 票券→攻佔)等委託人授權,需裝置的維持封閉。
