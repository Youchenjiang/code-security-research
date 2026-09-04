# Chable APK — Firebase 專案設定分析報告

**分析對象**: `chable/ChableApp/com.mgobill.chable.apk`（v2.2.8 / code 145）
**分析日期**: 2026-08-12
**分析方法**: 直接解析 APK 的 `resources.arsc` 字串池、`libapp.so`（Dart AOT）、dex、AndroidManifest.xml 與簽名區塊（apksigner）

---

## 1. App 基本資訊

| 項目 | 值 |
|---|---|
| 套件名稱 | `com.mgobill.chable` |
| 版本 | 2.2.8（versionCode 145） |
| App 名稱 | Chable |
| minSdk / targetSdk | 24 / 36（Android 16） |
| 框架 | Flutter（`libapp.so` + `libflutter.so` + `libdartjni.so`，ARM64 原生函式庫） |
| 上架狀態 | Google Play 上架（Play App Signing 簽名） |

## 2. Firebase 專案設定（google-services 注入值）

| 項目 | 值 |
|---|---|
| **project_id** | `chable-91c06` |
| **專案編號（gcm_defaultSenderId）** | `148101573582` |
| **google_app_id** | `1:148101573582:android:314a75ab3876716fded99f` |
| **google_api_key** | `AIzaSyARnsZGZA4bgCLdrifLnmI3DS_t_UW6jGQ` |
| google_crash_reporting_api_key | 與 google_api_key 相同 |
| default_web_client_id | `148101573582-7q1no34kqm31ieje3b84kdnbi1kaggc9.apps.googleusercontent.com` |
| google_storage_bucket | 未設定（空值） |
| Realtime Database URL | 未設定（無 `firebaseio.com`） |

> 注意：這些值對每個下載 APK 的人都是公開的（內嵌在 APK 裡），不是機密。

## 3. 使用的 Firebase 服務

| 服務 | 證據 |
|---|---|
| Cloud Firestore | 執行期 log 的 `cloud_firestore` 查詢、`Firestore: (26.4.0)`（SDK 版本 26.4.0） |
| Firebase Auth | 執行期 `FirebaseAuth: Notifying id token listeners` |
| Firebase Analytics | `FlutterFirebaseAppRegistrar`（analytics）+ 執行期 `FA-SVC` log |
| Cloud Functions | manifest 的 `io.flutter.plugins.firebase.functions.FlutterFirebaseAppRegistrar` |
| **App Check** | 見下節 |
| Firebase Messaging（可能） | manifest 有 `com.google.android.c2dm.permission.RECEIVE` |

## 4. App Check 詳細分析

| 項目 | 值 |
|---|---|
| **使用的 provider** | **Play Integrity** |
| Dart 端證據 | `libapp.so` 含 `AndroidPlayIntegrityProvider`、`_activateAppCheck`（main.dart:119） |
| Android 端證據 | dex 含 `FirebaseAppCheckPlayIntegrityRegistrar`、`fire-app-check-play-integrity`、`exchangePlayIntegrityToken` endpoint |
| 執行期證據 | log：`Integrity API error (-14): The Play Store needs to be updated` → 確定 playIntegrity provider 生效 |
| Token 傳遞 header | `X-Firebase-AppCheck` |
| 註冊綁定 | App Check 註冊綁定 **簽名憑證 SHA-256**（見 §5），改簽名即失效 |
| 其他 provider（未使用） | Debug / Recaptcha 的 registrar 與 endpoint 也存在（firebase-appcheck SDK 一併打包），但執行期證明未啟用 |

### App Check 為何在模擬器上必然失敗

- App Check 判定需 `PLAY_RECOGNIZED`（App 從 Google Play 安裝）或 `MEETS_DEVICE_INTEGRITY`（真機硬體認證）。
- 模擬器 + adb 側載：兩者皆無法達成 → 伺服器端 `PERMISSION_DENIED`，且 client 端任何修改都無法產生合法 token。
- 唯一解鎖管道：開發者 Firebase 主控台（關閉 enforcement 或註冊 debug token）。

## 5. 簽名資訊

| 項目 | 值 |
|---|---|
| 簽名方案 | V3（+ Source Stamp） |
| 簽名者 DN | `CN=Android, OU=Android, O=Google Inc., L=Mountain View, ST=California, C=US`（Google Play App Signing） |
| **簽名憑證 SHA-256** | `a66e72e13819534732dcc94549e10062647168823a4efc5677b322a06dcd5570` |
| 簽名憑證 SHA-1 | `c6795244887dcb7ce7cdaea4af2191605db95b49` |
| Source Stamp SHA-256 | `3257d599a49d2c961a471ca9843f59d341a405884583fc087df4237b733bbd6d` |

## 6. 內嵌第三方 SDK

| SDK | 證據 |
|---|---|
| Facebook（Audience Network） | `assets/audience_network/*.dex`、**facebook_app_id = `1234155308624062`**、manifest `com.facebook.sdk.ApplicationId` |
| Unity Ads | `UnityAds` class、`AdUnitActivity` 系列、執行期 `UnityAdsStorage` log |
| AdMob（可能） | manifest `com.google.android.gms.ads.APPLICATION_ID` |

## 7. Firestore 資料結構（執行期 log 觀察）

```
users/{uid}
users/{uid}/profile/settings
users/{uid}/profile/bank
users/{uid}/profile/tutorial
users/{uid}/profile/scan_inventory
users/{uid}/stores
users/{uid}/queued_actions      (where status == queued)
takeovers                       (where attackerUserId == uid / defenderUserId == uid)
```

## 8. 附註

- 擷取方法：`aapt2 dump resources`、`resources.arsc` 字串池比對、`apksigner verify --print-certs`、`libapp.so` 字串掃描、執行期 logcat 交叉驗證。
- 這份報告僅用於分析；API key 等值雖公開，仍不建議外洩於任何不受控環境。
