# 🔄 SIKANDER OS — MULTI-DEVICE SYNC & PWA ARCHITECTURE GUIDE
> **System**: Sikander OS (`ckndr/sikander-os`)  
> **Target Topology**: Home PC (Desktop/Workstation) ↔ Work PC (Corporate Laptop) ↔ Mobile Device (Android Chrome / iOS Safari PWA)  
> **Architecture**: Local-First, Offline-First, Zero-Cloud Lock-in, Zero Subscription Cost  

---

## 1. Architectural Philosophy: The "Sovereign Sync" Principle

Most personal productivity tools force you into costly monthly cloud subscriptions (Firebase, Supabase, Notion, Airtable) that compromise privacy, risk data loss if an account is suspended, and fail when you are offline in transit or in the gym.

**Sikander OS v2.0** uses a **Local-First, Multi-Device Sync Engine** (`data/sync_engine.js`):
1. **Local Speed & Zero Latency**: All changes (movie ratings, watchlist modifications, property receipts, music likes, gym logs, walk steps) are saved instantly to the local device's `LocalStorage` and `IndexedDB`.
2. **True Offline Independence**: With the Service Worker (`sw.js`), the entire application shell, styles, and datasets are pre-cached. You can use the app without cellular reception or WiFi.
3. **Multi-Device Parity**: Three flexible, zero-cost bridge mechanisms allow you to synchronize data seamlessly across Home PC, Work PC, and Phone.

---

## 2. The 3 Multi-Device Synchronization Bridges

```
                   ┌──────────────────────────────────────┐
                   │           GITHUB REPOSITORY          │
                   │         (ckndr/sikander-os)          │
                   │       GitHub Pages CDN Engine        │
                   └──────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │ Git Push / Pull       │ Automatic Deploy      │ Git Push / Pull
              ▼                       ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
    │     HOME PC      │    │  MOBILE PWA APP  │    │     WORK PC      │
    │  (I:\sikander-os)│    │ (Android / iOS)  │    │  (Local Clone)   │
    ├──────────────────┤    ├──────────────────┤    ├──────────────────┤
    │ Local-First IDB  │◄───┤ 1-Click JSON Sync│───►│ Local-First IDB  │
    │ Full Git Access  │    │ (Export / Import)│    │ Full Git Access  │
    └──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

### Bridge A: 1-Click PWA JSON Snapshot (Fastest for Mobile ↔ PC)

*Recommended for daily mobile updates (e.g. logging walks, gym sets, or movie watchlist adds on your phone).*

1. **On your Phone**:
   - Tap the bottom navigation bar **Sync (🔄)** icon.
   - Tap **"📦 1-Click Export Data Snapshot (.json)"**.
   - Your phone saves `sikander_os_sync_YYYY-MM-DD_Android.json`.
   - Send this tiny file (< 50 KB) to your PC via WhatsApp, Telegram "Saved Messages", or Google Drive.
2. **On your PC**:
   - Open Sikander OS on your PC.
   - Click the bottom bar **Sync (🔄)** icon or topbar status badge.
   - Click **"📥 1-Click Import Data Snapshot (.json)"** and choose the downloaded file.
   - Sikander OS instantly merges the keys with your local environment with zero data loss!

---

### Bridge B: GitHub Pages Sovereign Bridge (Home PC ↔ Work PC)

*Recommended for permanent master catalog updates (e.g., adding new movie datasets, updating the property ledger, or adding pay slips).*

1. **Master Repository on GitHub**:
   - The repository `ckndr/sikander-os` is hosted on GitHub with **GitHub Pages** enabled on the `main` branch.
2. **Home PC Workflow**:
   ```bash
   # Make changes or ingest new data
   git add .
   git commit -m "Update property receipts and cinema watchlist"
   git push origin main
   ```
3. **Work PC Workflow**:
   ```bash
   # Fetch latest changes when starting work
   git pull origin main
   ```
4. **Mobile Benefit**:
   - Because GitHub Pages updates within 60 seconds of a push, visiting the GitHub Pages URL on your phone automatically triggers the Service Worker's Stale-While-Revalidate cycle, updating the cache transparently in the background!

---

### Bridge C: Google Drive / Cloud Vault Folder Sync (Zero-Command Line)

*For syncing binary receipts, large exports, or SQLite files without Git:*
- Keep `data/` backup exports in a Google Drive folder (`Google Drive/Sikander_OS_Vault/`).
- Import directly into any browser with 1 click.

---

## 3. PWA Installation Instructions

### Android (Google Chrome / Brave / Edge):
1. Navigate to the Sikander OS URL.
2. You will see an in-app banner: **"Install Sikander OS — Install standalone native app for offline life cockpit"**.
3. Tap **"Install"**.
4. Alternatively, tap the 3-dots menu in Chrome $\rightarrow$ **"Install app"** / **"Add to Home screen"**.
5. The Sikander OS icon (Obsidian/Cyan Gem) will appear on your app drawer and home screen.
6. The app opens full-screen without address bars or browser tabs, functioning like a native Kotlin/Java app.

### iOS (Safari on iPhone / iPad):
1. Open the Sikander OS URL in **Safari**.
2. Tap the **Share** button (rectangle with upward arrow $\uparrow$) in the bottom toolbar.
3. Scroll down and select **"Add to Home Screen"** ($+$).
4. Name: "Sikander OS" $\rightarrow$ Tap **Add**.
5. Sikander OS launches standalone with safe-area notch support, black translucent status bars, and full offline caching via Service Worker.

---

## 4. Troubleshooting & Verification

- **Checking Service Worker Status**: Open DevTools (`F12` or `Ctrl+Shift+I`) $\rightarrow$ **Application** tab $\rightarrow$ **Service Workers**. Status should show `Activated and is running`.
- **Testing Offline Mode**: In DevTools, go to **Network** tab $\rightarrow$ set throttling dropdown to **Offline** $\rightarrow$ refresh the page. The app loads instantly from cache.
- **Forcing a Cache Invalidation**: Tap the bottom bar **Sync (🔄)** icon $\rightarrow$ tap "Reset / Purge Local Cache", or update `CACHE_NAME` in `sw.js`.
