# 模擬器 Play Store 安裝實驗(2026-08-14)

> 目標:判斷 App Check 是否只要求 app integrity(唯一純軟體解鎖路)。
> 方法:android-35 `google_apis_playstore` 映像 → 登入 Play 帳號 → 從商店安裝 Chable → 觀察 App Check token 是否成功。
> **結論(已完成):純軟體路**確定封死**——三條路徑全部實測封閉,App Check verdict 已觀察到(403 App attestation failed)。唯一路 = 真機 Play 安裝。**
> **2026-08-15 補充:真機路亦已由委託方終止 → 至此所有裝置路全關。**

---

## 1. 環境調校(已解決先前的崩潰)

| 參數 | 之前 | 現在 | 結果 |
|---|---|---|---|
| 映像 | android-35 playstore | 同(唯一改 AVD `config.ini`) | 原生 x86_64 + WHPX 加速 |
| RAM | 2048 MB | **4096 MB**(`hw.ramSize=4096`) | boot 30 秒、系統穩定 |
| 核心 | 預設 | 4(`hw.cpu.ncore=4`) | 無 Launcher ANR |
| 啟動 | 一般 | `-no-snapshot -no-audio -no-boot-anim -gpu swiftshader_indirect -no-window` | 無崩潰 |

- 先前「ARM 轉譯下崩潰」的根因是 **2G RAM + 系統過載**,不是 ARM 轉譯本身;4G 下 app 正常啟動、Flutter engine 載入、GMS 26.29.32 + Play Store 52.6.26 都健康。
- 注意:app 只有 arm64/armeabi-v7a split,**沒有 x86_64** → 一定走 ARM 轉譯(慢但可用)。
- 冷開機(-no-snapshot)後 1–2 分鐘內啟動器/System UI 可能 ANR,等系統安定後再操作。

## 2. Sideload 對照組實測(健康環境,首次完整觀察到)

`adb install-multiple` 裝 base+arm64+en+xxhdpi(v2.2.8,installer=null)→ 啟動 → logcat 完整時間線:

```
06:27:46  FirebaseApp: initializing all Firebase APIs
06:27:51  D LicenseClient: Connecting to the main licensing service...   ← 閘門 1:Play Licensing (LVL)
06:27:52  D LicenseClient: Sending request to licensing service...
06:27:53  I PlayCore: IntegrityService : requestIntegrityToken(cloudProjectNumber=148101573582)  ← 閘門 2:App Check
06:27:58  I Finsky: Integrity key attestation record generated successfully.   ← GMS 端產生成功
06:27:57  I .mgobill.chable: System.exit called, status: 0                    ← 無授權 → app 自殺(clean exit)
06:28:13  E Finsky: requestIntegrityToken() failed ... DeadObjectException     ← 回傳 binder 打到已死的 app
```

**關鍵發現:app 啟動有兩道閘門,不是一道:**

1. **LVL 授權檢查**(`LicenseClient` + `System.exit(0)`)— app 送授權請求後 ~4.7 秒沒拿到 LICENSED 就自動退出。沒有 Play 帳號的裝置 → 必退。
2. **App Check / Play Integrity**(`requestIntegrityToken`)— 這次在 healthy 環境下 GMS 端「attestation record generated successfully」,但回傳時 app 已被 LVL 閘門自殺 → DeadObjectException,不是 verdict 拒絕。

> 這同時推翻了上次「sideload 一定拿不到 PLAY_RECOGNIZED」的結論——**從來沒觀察到 verdict,因為 app 先被 LVL 殺掉**。真正的 sideload verdict 仍未觀察到,但已無關緊要(見 §4)。

## 3. `adb install -i com.android.vending` spoof 已排除

- 想法:spoof installer-of-record 騙 app-recognition。
- 排除理由:LVL 授權檢查是**帳號層**的(license service 用裝置上的 Google 帳號判斷),跟 installer 是誰無關。沒有帳號 → LVL 必退,spoof 與否不影響。
- 死因是 LVL,不是 integrity。

> **⚠️ §3 的排除理由事後證明不完整**(見 §4 的完整 verdict 實驗):spoof 確實能騙過 app 的**本機** installer 檢查,只是最後仍死在 App Check 的 403。

## 4. 完整 verdict 實驗(2026-08-14,帳號已登入)

**前置**:`g1014308gg@gmail.com` 已登入模擬器(卡點 §5 解除)。三條路徑依序實測:

### 4a. Play Store 安裝 — 🚫 商店層封鎖

Play Store 開啟 Chable 頁面(`market://details?id=com.mgobill.chable`,帳號已登入)→ 畫面顯示
**「這個應用程式僅適用於其他裝置」** + 只有「安裝到其他裝置」(OPPO/Xiaomi/Redmi)按鈕,
**本機沒有 Install 按鈕**(原本顯示「解除安裝」,因 sideload 版存在)。解除安裝後仍只有其他裝置按鈕。

- APK 檢查:base 無 native-code;`config.arm64_v8a.apk` = `native-code: 'arm64-v8a'`(無 x86_64)。
- 裝置 abilist = `x86_64,arm64-v8a`(有轉譯,ABI 面看似相容)→ 封鎖非 ABI 面,是 **Play 裝置相容性過濾**。
- **結論:Play Store 不讓模擬器安裝 Chable → PLAY_RECOGNIZED 這條路在模擬器上從根源斷絕。**

### 4b. Sideload + 帳號 — 🚫 新發現:app 本機 installer 檢查

重裝 sideload(installer=null)+ 帳號在 → logcat:

```
07:37:09  LicenseClient: Local install check failed due to wrong installer.   ← ★ 本機檢查:installer 不是 com.android.vending
07:37:13  LicenseClient: Sending request to licensing service...
07:37:14  System.exit called, status: 0                                       ← 本機檢查失敗 → 自殺,App Check 未到達
```

**新發現:app 除了伺服器 LVL,還做本機 installer-of-record 檢查**(`Local install check failed due to wrong installer`)。
sideload(installer=null)連 LVL 伺服器回應都不用等就退出。這是先前「死因是 LVL」的完整化:死因是
「本機 installer 檢查」+ 伺服器 LVL 雙重閘門。

### 4c. `install -i com.android.vending` spoof — 🚫 App Check verdict 終於觀察到

uninstall 後 `adb install-multiple -i com.android.vending ...`(installerPackageName 變 `com.android.vending`)+ 帳號在:

```
07:38:20  LicenseClient: Sending request to license reporting service...        ← 本機檢查過、LVL 過(帳號 LICENSED)
07:38:21  requestIntegrityToken(cloudProjectNumber=148101573582)                ← 抵達 App Check
07:38:22  Integrity key attestation record generated successfully                ← GMS 端產生 token
07:38:24  requestIntegrityToken() finished / onRequestIntegrityToken            ← token 回傳 app
07:38:25  ★ App Check activation failed: [firebase_app_check/unknown] code: 403 body: App attestation failed.
07:38:35  Firestore Listen failed: PERMISSION_DENIED(industries、app_config/rollover_status、app_config/admin_settings)
07:38:35  flutter: FATAL ZoneError → app 崩潰
```

**這就是從未觀察到的 App Check verdict**:Play Integrity token 產生了,但 **Firebase App Check 拒絕認證**
(`403 App attestation failed`)——spoof 的 installer 拿不到 `PLAY_RECOGNIZED`,模擬器也沒有
`MEETS_DEVICE_INTEGRITY` → token 無效 → Firestore 全 `PERMISSION_DENIED` → app FATAL 崩潰。

**結論:App Check(Play Integrity)**確定**要求「真 Play 安裝或真機硬體認證」,純軟體路(模擬器)在
任何變體下都拿不到合法 token。**唯一可行路 = 真機 + Play Store 安裝**(`真機掃描驗證步驟.md`)
——該路已於 **2026-08-15 由委託方終止**,至此全路關閉。

## 5. 卡點(已解除,結果為負面)

**原卡點:需要一個 Google 帳號(email+password)登入模擬器。** 2026-08-14 已登入
`g1014308gg@gmail.com` → 卡點解除 → §4 三路徑實測 → **純軟體路封死**。真機套件
(`bot/scan-verify.js --buy` + `真機掃描驗證步驟.md`)**自 2026-08-15 起隨真機路終止而停用**。

## 6. 順帶觀察:rollover 時間異常

- watch(PID 377140)持續健康:08-14 06:29 UTC 已 poll#434,全 200 無 401。
- **08-14 04:00 UTC(先前推測的 EDT 午夜)沒有 rollover**——06:29 UTC 仍 `gameDay=20260813`。
- 推測改為 ~07:00 UTC(Pacific 午夜)或伺服器 daily job 延遲;watch 每 3 分鐘輪詢,flip 當下會自動跑完整 post-rollover 套件,不影響本實驗。

> **08-14 補充**:07:22 UTC probe-marketplace 已觀察到 `gameDay=20260814`(rollover 已發生,
> 落在 06:53–07:22 之間,即 ~07:00 UTC 附近);watch 已證實連續兩天。(後續更新:`loa-day1-watch-20260814` 最後記錄 06:53 UTC 仍 20260813。)
