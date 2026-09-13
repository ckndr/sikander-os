/**
 * Sikander OS — Local-First Multi-Device Sync Engine & PWA Core
 * Repository: ckndr/sikander-os
 * Manages LocalStorage & IndexedDB storage, JSON snapshot export/import,
 * Service Worker registration, mobile bottom navigation, and PWA installation.
 */

(function (window, document) {
  'use strict';

  const SYNC_ENGINE_VERSION = '2.0.0';
  const DB_NAME = 'SikanderOS_DB';
  const DB_VERSION = 1;
  const STORE_NAME = 'sync_snapshots';

  // State
  let deferredInstallPrompt = null;
  let dbInstance = null;

  // Initialize IndexedDB
  function initDB() {
    return new Promise((resolve) => {
      if (!window.indexedDB) {
        console.warn('[Sikander Sync] IndexedDB not available, using LocalStorage only.');
        resolve(null);
        return;
      }
      const req = window.indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
        }
      };
      req.onsuccess = (e) => {
        dbInstance = e.target.result;
        resolve(dbInstance);
      };
      req.onerror = () => {
        console.warn('[Sikander Sync] Failed to open IndexedDB.');
        resolve(null);
      };
    });
  }

  // Save snapshot to IndexedDB
  async function persistSnapshotToIDB(snapshot) {
    if (!dbInstance) await initDB();
    if (!dbInstance) return;
    try {
      const tx = dbInstance.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      store.add({
        timestamp: new Date().toISOString(),
        snapshot: snapshot
      });
    } catch (e) {
      console.warn('[Sikander Sync] IndexedDB snapshot error:', e);
    }
  }

  // Generate or retrieve persistent Device Identifier
  function getDeviceId() {
    let devId = localStorage.getItem('sikander_device_id');
    if (!devId) {
      const platform = /iPhone|iPad|iPod/i.test(navigator.userAgent) ? 'iOS' :
                       /Android/i.test(navigator.userAgent) ? 'Android' :
                       /Mac/i.test(navigator.userAgent) ? 'macOS' :
                       /Win/i.test(navigator.userAgent) ? 'Windows' : 'Device';
      devId = `${platform}-${Math.random().toString(36).substring(2, 7).toUpperCase()}`;
      localStorage.setItem('sikander_device_id', devId);
    }
    return devId;
  }

  // Master Sync Engine Object
  const SikanderSync = {
    version: SYNC_ENGINE_VERSION,

    // Initialize core features
    async init() {
      await initDB();
      this.registerServiceWorker();
      this.setupInstallPrompt();
      this.setupNetworkWatchers();
      this.setupPrivacyWatchers();
      this.setupGlobalKeyboardShortcuts();
      this.injectStyles();
      this.injectMobileNav();
      this.injectSyncModal();
      this.updateStatusBadges();
      this.applyPrivacyToPage();
      console.log(`[Sikander OS] Sync Engine & PWA Core v${SYNC_ENGINE_VERSION} Active (Device: ${getDeviceId()})`);
    },

    // Register Service Worker
    registerServiceWorker() {
      if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('./sw.js')
            .then((reg) => {
              console.log('[Sikander OS] Service Worker registered with scope:', reg.scope);
              reg.onupdatefound = () => {
                const installingWorker = reg.installing;
                installingWorker.onstatechange = () => {
                  if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    this.showToast('✨ New Sikander OS update available! Refresh to activate.');
                  }
                };
              };
            })
            .catch((err) => {
              console.warn('[Sikander OS] Service Worker registration failed:', err);
            });
        });
      }
    },

    // Setup PWA Installation Prompt
    setupInstallPrompt() {
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredInstallPrompt = e;
        console.log('[Sikander OS] PWA installation available.');
        this.showInstallBanner();
      });

      window.addEventListener('appinstalled', () => {
        deferredInstallPrompt = null;
        this.hideInstallBanner();
        this.showToast('🚀 Sikander OS installed successfully!');
      });
    },

    promptInstall() {
      if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        deferredInstallPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            console.log('[Sikander OS] User accepted PWA install.');
          }
          deferredInstallPrompt = null;
          this.hideInstallBanner();
        });
      } else {
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        if (isIOS) {
          alert("To install Sikander OS on iOS Safari:\n1. Tap the 'Share' icon (square with arrow up)\n2. Scroll down and tap 'Add to Home Screen' (+)\n3. Tap 'Add' in top right.");
        } else {
          this.showToast('Sikander OS is already installed or your browser does not support automated prompt.');
        }
      }
    },

    showInstallBanner() {
      if (localStorage.getItem('sikander_install_dismissed') === 'true') return;
      let banner = document.getElementById('sikander-install-banner');
      if (banner) {
        banner.style.display = 'flex';
      }
    },

    hideInstallBanner() {
      const banner = document.getElementById('sikander-install-banner');
      if (banner) {
        banner.style.display = 'none';
      }
    },

    dismissInstallBanner() {
      this.hideInstallBanner();
      localStorage.setItem('sikander_install_dismissed', 'true');
    },

    // Setup Online/Offline Status Watchers
    setupNetworkWatchers() {
      window.addEventListener('online', () => {
        this.updateStatusBadges();
        this.showToast('🟢 Back Online — Cloud sync bridge ready.');
      });
      window.addEventListener('offline', () => {
        this.updateStatusBadges();
        this.showToast('⚡ Offline Mode Active — Operating from Sovereign Cache.');
      });
    },

    updateStatusBadges() {
      const isOnline = navigator.onLine;
      const statusBadges = document.querySelectorAll('.status-badge');
      statusBadges.forEach((badge) => {
        const dot = badge.querySelector('.status-dot') || badge.querySelector('span:first-child');
        const label = badge.querySelector('span:last-child');
        if (isOnline) {
          badge.style.background = 'rgba(16, 185, 129, 0.1)';
          badge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
          badge.style.color = '#10b981';
          if (label) label.textContent = 'SYSTEM ACTIVE';
          if (dot) {
            dot.style.background = '#10b981';
            dot.style.boxShadow = '0 0 10px #10b981';
          }
        } else {
          badge.style.background = 'rgba(245, 158, 11, 0.12)';
          badge.style.borderColor = 'rgba(245, 158, 11, 0.4)';
          badge.style.color = '#f59e0b';
          if (label) label.textContent = 'OFFLINE CACHE';
          if (dot) {
            dot.style.background = '#f59e0b';
            dot.style.boxShadow = '0 0 10px #f59e0b';
          }
        }
      });
    },

    // Global Privacy Mode Management
    setupPrivacyWatchers() {
      window.addEventListener('storage', (e) => {
        if (e.key === 'sikander_privacy_mode' || e.key === 'sikander_finance_privacy') {
          this.applyPrivacyToPage();
        }
      });
      window.addEventListener('sikander-privacy-change', () => {
        this.applyPrivacyToPage();
      });
    },

    getPrivacyMode() {
      return localStorage.getItem('sikander_privacy_mode') === '1' ||
             localStorage.getItem('sikander_finance_privacy') === '1';
    },

    setPrivacyMode(active, notify = true) {
      localStorage.setItem('sikander_privacy_mode', active ? '1' : '0');
      localStorage.setItem('sikander_finance_privacy', active ? '1' : '0');
      this.applyPrivacyToPage();
      window.dispatchEvent(new CustomEvent('sikander-privacy-change', { detail: { active } }));
      if (notify) {
        this.showToast(active ? '🔒 Global Privacy Shield: ON (Figures Masked)' : '👁️ Global Privacy Shield: OFF (Figures Exposed)');
      }
    },

    togglePrivacy() {
      this.setPrivacyMode(!this.getPrivacyMode(), true);
    },

    applyPrivacyToPage() {
      const active = this.getPrivacyMode();
      
      // 1. Generic maskable numbers
      document.querySelectorAll('.privacy-maskable, .comp-maskable').forEach((el) => {
        if (!el.getAttribute('data-real-val')) {
          el.setAttribute('data-real-val', el.innerHTML.trim());
        }
        const raw = el.getAttribute('data-real-val');
        if (active) {
          if (raw === '-' || raw === '—' || raw === 'N/A' || raw === '') {
            el.innerHTML = raw;
          } else if (raw.includes('Bank') && raw.includes('Property')) {
            el.innerHTML = 'Bank PKR •••••• · Property PKR •••••• (67% Equity)';
          } else if (raw.startsWith('PKR')) {
            el.innerHTML = 'PKR ••••••';
          } else {
            el.innerHTML = '••••••';
          }
        } else {
          el.innerHTML = raw;
        }
      });

      // 2. Account numbers / sensitive strings
      document.querySelectorAll('.privacy-maskable-acc').forEach((el) => {
        if (!el.getAttribute('data-real-val')) {
          el.setAttribute('data-real-val', el.textContent.trim());
        }
        const raw = el.getAttribute('data-real-val');
        if (active) {
          if (raw.startsWith('N/A')) el.textContent = 'N/A';
          else if (raw.length > 4) el.textContent = '••••••••' + raw.slice(-4);
          else el.textContent = '••••••';
        } else {
          el.textContent = raw;
        }
      });

      // 3. Update buttons and icons across current page
      const btnIds = ['privacy-toggle-btn', 'global-privacy-btn', 'dock-privacy-btn'];
      btnIds.forEach((id) => {
        const btn = document.getElementById(id);
        if (btn) {
          if (active) {
            btn.classList.add('active');
            btn.classList.remove('unmasked');
          } else {
            btn.classList.remove('active');
            btn.classList.add('unmasked');
          }
        }
      });
      const iconIds = ['privacy-icon', 'global-privacy-icon'];
      iconIds.forEach((id) => {
        const icon = document.getElementById(id);
        if (icon) icon.textContent = active ? '🔒' : '👁️';
      });
      const textIds = ['privacy-text', 'global-privacy-text'];
      textIds.forEach((id) => {
        const text = document.getElementById(id);
        if (text) text.textContent = active ? 'Privacy Mode: ON' : 'Privacy Mode: OFF';
      });
      
      // 4. Trigger page specific renderers
      if (typeof window.applyPrivacy === 'function' && window.isPrivacyMode !== active) {
        window.isPrivacyMode = active;
        try { window.applyPrivacy(); } catch (e) {}
      }
      if (typeof window.renderCompensationTable === 'function' && window.privacyMode !== active) {
        window.privacyMode = active;
        const chartWrap = document.getElementById('salary-chart');
        if (chartWrap) {
          if (active) chartWrap.classList.add('privacy-blurred');
          else chartWrap.classList.remove('privacy-blurred');
        }
        try { window.renderCompensationTable(); } catch (e) {}
      }
    },

    // Collect all Sikander OS local data into a JSON snapshot
    createSnapshot() {
      const data = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        // Collect all related keys
        if (
          key.startsWith('sikander_') ||
          key.startsWith('cinema_') ||
          key.startsWith('music_') ||
          key.startsWith('property_') ||
          key.startsWith('health_') ||
          key.startsWith('career_') ||
          key.startsWith('finance_')
        ) {
          try {
            data[key] = JSON.parse(localStorage.getItem(key));
          } catch (e) {
            data[key] = localStorage.getItem(key);
          }
        }
      }

      return {
        app: 'Sikander OS',
        system: 'Sovereign Life Command Center',
        version: SYNC_ENGINE_VERSION,
        exportedAt: new Date().toISOString(),
        deviceId: getDeviceId(),
        itemCount: Object.keys(data).length,
        payload: data
      };
    },

    // Export Snapshot as downloadable JSON file
    exportSnapshot() {
      const snapshot = this.createSnapshot();
      const dateStr = new Date().toISOString().slice(0, 10);
      const filename = `sikander_os_sync_${dateStr}_${getDeviceId()}.json`;
      const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      persistSnapshotToIDB(snapshot);
      localStorage.setItem('sikander_last_sync_export', new Date().toISOString());
      this.showToast(`📦 Exported ${snapshot.itemCount} records to ${filename}`);
      this.renderSyncStats();
    },

    // Import Snapshot from JSON string
    async importSnapshot(jsonString, mode = 'merge') {
      try {
        const data = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
        if (!data || (!data.payload && typeof data !== 'object')) {
          throw new Error('Invalid Sikander OS snapshot format.');
        }

        const payload = data.payload || data;
        let count = 0;

        if (mode === 'overwrite') {
          // Clear previous keys
          const keysToRemove = [];
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('sikander_') && key !== 'sikander_device_id') {
              keysToRemove.push(key);
            }
          }
          keysToRemove.forEach((k) => localStorage.removeItem(k));
        }

        for (const [key, value] of Object.entries(payload)) {
          const valStr = typeof value === 'object' ? JSON.stringify(value) : String(value);
          localStorage.setItem(key, valStr);
          count++;
        }

        localStorage.setItem('sikander_last_sync_import', new Date().toISOString());
        await persistSnapshotToIDB(data);

        this.showToast(`✅ Successfully imported ${count} items from ${data.deviceId || 'External Device'}!`);
        this.renderSyncStats();

        // Refresh UI state after short delay
        setTimeout(() => {
          window.location.reload();
        }, 1200);

        return true;
      } catch (err) {
        console.error('[Sikander Sync] Import failed:', err);
        alert('Sync Import Failed: ' + err.message);
        return false;
      }
    },

    // Storage and Telemetry Statistics
    getStats() {
      let itemCount = 0;
      let totalBytes = 0;
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (
          key.startsWith('sikander_') ||
          key.startsWith('cinema_') ||
          key.startsWith('music_') ||
          key.startsWith('property_')
        ) {
          itemCount++;
          const val = localStorage.getItem(key) || '';
          totalBytes += (key.length + val.length) * 2;
        }
      }

      return {
        itemCount,
        totalBytes,
        formattedSize: totalBytes > 1024 * 1024 ?
          (totalBytes / (1024 * 1024)).toFixed(2) + ' MB' :
          (totalBytes / 1024).toFixed(1) + ' KB',
        deviceId: getDeviceId(),
        lastExport: localStorage.getItem('sikander_last_sync_export') || 'Never',
        lastImport: localStorage.getItem('sikander_last_sync_import') || 'Never',
        isPwaStandalone: window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true
      };
    },

    renderSyncStats() {
      const stats = this.getStats();
      const statsContainer = document.getElementById('sync-stats-container');
      if (statsContainer) {
        statsContainer.innerHTML = `
          <div class="sync-stat-pill">
            <span class="sync-stat-label">Device ID</span>
            <span class="sync-stat-val">${stats.deviceId}</span>
          </div>
          <div class="sync-stat-pill">
            <span class="sync-stat-label">Sync Items</span>
            <span class="sync-stat-val">${stats.itemCount}</span>
          </div>
          <div class="sync-stat-pill">
            <span class="sync-stat-label">Local Data Size</span>
            <span class="sync-stat-val">${stats.formattedSize}</span>
          </div>
          <div class="sync-stat-pill">
            <span class="sync-stat-label">PWA Mode</span>
            <span class="sync-stat-val" style="color: ${stats.isPwaStandalone ? '#10b981' : '#00f2fe'};">
              ${stats.isPwaStandalone ? 'Standalone App' : 'Browser Web'}
            </span>
          </div>
        `;
      }
    },

    openSyncModal() {
      const modal = document.getElementById('sikander-sync-modal');
      if (modal) {
        this.renderSyncStats();
        modal.style.display = 'flex';
      }
    },

    closeSyncModal() {
      const modal = document.getElementById('sikander-sync-modal');
      if (modal) {
        modal.style.display = 'none';
      }
      const shortcutsModal = document.getElementById('sikander-shortcuts-modal');
      if (shortcutsModal) {
        shortcutsModal.style.display = 'none';
      }
    },

    openHelpModal() {
      let modal = document.getElementById('sikander-shortcuts-modal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'sikander-shortcuts-modal';
        modal.className = 'sikander-sync-modal-backdrop';
        modal.style.zIndex = '10050';
        modal.onclick = (e) => {
          if (e.target === modal) modal.style.display = 'none';
        };
        modal.innerHTML = `
          <div class="sikander-sync-modal-box" style="max-width: 580px;">
            <div class="sync-modal-header">
              <div class="sync-modal-title">
                <span>⌨️</span> Sikander OS Universal Shortcuts
              </div>
              <button class="btn-install-dismiss" onclick="document.getElementById('sikander-shortcuts-modal').style.display='none'">✕</button>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:16px;">
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🎬 Cinema Hub</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">1</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🏢 Property Ledger</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">2</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🎵 Music Hub</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">3</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>💼 Career Cockpit</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">4</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🏦 Capital & Finance</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">5</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🏃 Health & Vitality</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">6</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🔍 Universal Search</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">Ctrl+K</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>🔒 Privacy Shield</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">P</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>❓ Shortcuts Help</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">?</kbd></div>
              <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:12px;"><span>✕ Close Modal</span><kbd style="color:#00f2fe; font-family:monospace; font-weight:700;">Esc</kbd></div>
            </div>
            <div style="text-align:right;">
              <button class="btn-install-trigger" onclick="document.getElementById('sikander-shortcuts-modal').style.display='none'" style="font-size:12px; padding:6px 16px;">Close (Esc)</button>
            </div>
          </div>
        `;
        document.body.appendChild(modal);
      }
      modal.style.display = 'flex';
    },

    setupGlobalKeyboardShortcuts() {
      const path = (window.location.pathname || '').toLowerCase();
      const isHome = path.endsWith('index.html') || path.endsWith('/') || path === '';

      // If on index.html, index.html already implements its own rich palette and shortcuts
      if (isHome) return;

      document.addEventListener('keydown', (e) => {
        const isInput = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable;

        // Escape closes any open sync/shortcuts modal
        if (e.key === 'Escape') {
          this.closeSyncModal();
          return;
        }

        // Ctrl+K or Cmd+K: Universal Command Palette (redirects to index.html#palette)
        if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
          e.preventDefault();
          window.location.href = 'index.html#palette';
          return;
        }

        const syncModal = document.getElementById('sikander-sync-modal');
        const isSyncOpen = syncModal && syncModal.style.display === 'flex';
        const scModal = document.getElementById('sikander-shortcuts-modal');
        const isScOpen = scModal && scModal.style.display === 'flex';
        if (isInput || isSyncOpen || isScOpen) return;

        if (e.key === '1') {
          e.preventDefault();
          window.location.href = 'cinema.html';
        } else if (e.key === '2') {
          e.preventDefault();
          window.location.href = 'finance.html#property';
        } else if (e.key === '3') {
          e.preventDefault();
          window.location.href = 'music.html';
        } else if (e.key === '4') {
          e.preventDefault();
          window.location.href = 'career.html';
        } else if (e.key === '5') {
          e.preventDefault();
          window.location.href = 'finance.html';
        } else if (e.key === '6') {
          e.preventDefault();
          window.location.href = 'health.html';
        } else if (e.key === 'p' || e.key === 'P') {
          e.preventDefault();
          this.togglePrivacy();
        } else if (e.key === '?') {
          e.preventDefault();
          this.openHelpModal();
        }
      });
    },

    // Inject shared CSS styles
    injectStyles() {
      if (document.getElementById('sikander-sync-styles')) return;
      const style = document.createElement('style');
      style.id = 'sikander-sync-styles';
      style.textContent = `
        /* Mobile Bottom Floating Navigation Bar */
        .sikander-bottom-nav {
          position: fixed;
          bottom: 12px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 9999;
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          background: rgba(10, 14, 24, 0.92);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(0, 242, 254, 0.25);
          border-radius: 36px;
          box-shadow: 0 10px 35px rgba(0, 0, 0, 0.7), 0 0 20px rgba(0, 242, 254, 0.15);
          max-width: calc(100vw - 24px);
          padding-bottom: max(8px, env(safe-area-inset-bottom));
        }

        .sikander-nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-width: 52px;
          min-height: 46px;
          padding: 4px 8px;
          border-radius: 20px;
          color: #94a3b8;
          text-decoration: none;
          font-size: 10px;
          font-weight: 600;
          letter-spacing: 0.02em;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          touch-action: manipulation;
          border: none;
          background: transparent;
          cursor: pointer;
        }

        .sikander-nav-item .nav-icon {
          font-size: 18px;
          line-height: 1.2;
          margin-bottom: 2px;
          transition: transform 0.2s ease;
        }

        .sikander-nav-item:hover,
        .sikander-nav-item:focus {
          color: #f1f5f9;
        }

        .sikander-nav-item:hover .nav-icon {
          transform: translateY(-2px);
        }

        .sikander-nav-item.active {
          color: #00f2fe;
          background: rgba(0, 242, 254, 0.12);
          border: 1px solid rgba(0, 242, 254, 0.3);
          box-shadow: 0 0 14px rgba(0, 242, 254, 0.25);
        }

        /* In-App Mobile Install Banner */
        .sikander-install-banner {
          position: fixed;
          top: 14px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 10000;
          width: calc(100% - 28px);
          max-width: 520px;
          background: rgba(13, 18, 30, 0.96);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(0, 242, 254, 0.35);
          border-radius: 18px;
          padding: 12px 16px;
          display: none;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          box-shadow: 0 15px 40px rgba(0,0,0,0.8), 0 0 25px rgba(0, 242, 254, 0.2);
          animation: bannerSlideDown 0.35s ease-out;
        }

        @keyframes bannerSlideDown {
          from { opacity: 0; transform: translate(-50%, -20px); }
          to { opacity: 1; transform: translate(-50%, 0); }
        }

        .install-banner-left {
          display: flex;
          align-items: center;
          gap: 12px;
          overflow: hidden;
        }

        .install-gem {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          background: linear-gradient(135deg, #00f2fe 0%, #8b5cf6 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          flex-shrink: 0;
          box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        }

        .install-texts h4 {
          font-size: 13.5px;
          font-weight: 700;
          color: #fff;
          margin: 0;
          line-height: 1.3;
        }

        .install-texts p {
          font-size: 11px;
          color: #94a3b8;
          margin: 0;
          line-height: 1.2;
        }

        .install-banner-actions {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }

        .btn-install-trigger {
          background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
          color: #050811;
          font-weight: 800;
          font-size: 12px;
          padding: 8px 14px;
          border-radius: 10px;
          border: none;
          cursor: pointer;
          min-height: 38px;
          box-shadow: 0 0 15px rgba(0, 242, 254, 0.35);
          touch-action: manipulation;
        }

        .btn-install-dismiss {
          background: transparent;
          color: #64748b;
          border: none;
          font-size: 18px;
          width: 34px;
          height: 34px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
        }
        .btn-install-dismiss:hover {
          color: #f1f5f9;
        }

        /* Sync Modal */
        .sikander-sync-modal-backdrop {
          display: none;
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.82);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          z-index: 10001;
          align-items: center;
          justify-content: center;
          padding: 16px;
        }

        .sikander-sync-modal-box {
          background: #0d121f;
          border: 1px solid rgba(0, 242, 254, 0.3);
          border-radius: 20px;
          max-width: 580px;
          width: 100%;
          max-height: 88vh;
          overflow-y: auto;
          padding: 24px;
          position: relative;
          color: #f1f5f9;
          box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 35px rgba(0, 242, 254, 0.15);
        }

        .sync-modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
          padding-bottom: 14px;
        }

        .sync-modal-title {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 18px;
          font-weight: 800;
        }

        .sync-stat-strip {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
          gap: 10px;
          margin-bottom: 20px;
        }

        .sync-stat-pill {
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 12px;
          padding: 10px;
          text-align: center;
        }

        .sync-stat-label {
          font-size: 10px;
          color: #64748b;
          text-transform: uppercase;
          display: block;
          margin-bottom: 4px;
          font-weight: 700;
        }

        .sync-stat-val {
          font-size: 13px;
          font-weight: 800;
          color: #f1f5f9;
          font-family: monospace;
        }

        .sync-action-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          width: 100%;
          padding: 12px 18px;
          border-radius: 12px;
          font-weight: 700;
          font-size: 14px;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
          min-height: 48px;
          margin-bottom: 10px;
          touch-action: manipulation;
        }

        .btn-export-sync {
          background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
          color: #050811;
          box-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        }
        .btn-export-sync:hover {
          transform: translateY(-2px);
          box-shadow: 0 0 25px rgba(0, 242, 254, 0.5);
        }

        .btn-import-sync {
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid rgba(255, 255, 255, 0.15);
          color: #fff;
        }
        .btn-import-sync:hover {
          background: rgba(255, 255, 255, 0.12);
        }

        .sync-guide-box {
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
          padding: 14px;
          font-size: 12px;
          line-height: 1.6;
          color: #94a3b8;
          margin-top: 18px;
        }

        .sync-guide-box h5 {
          color: #00f2fe;
          font-size: 12.5px;
          margin-bottom: 6px;
        }

        /* Toast Container */
        .sikander-toast {
          position: fixed;
          bottom: 76px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 10002;
          background: rgba(13, 18, 30, 0.95);
          border: 1px solid rgba(0, 242, 254, 0.4);
          color: #f1f5f9;
          padding: 10px 20px;
          border-radius: 30px;
          font-size: 13px;
          font-weight: 600;
          box-shadow: 0 10px 30px rgba(0,0,0,0.8);
          pointer-events: none;
          display: none;
          animation: toastIn 0.3s ease;
        }

        @keyframes toastIn {
          from { opacity: 0; transform: translate(-50%, 15px); }
          to { opacity: 1; transform: translate(-50%, 0); }
        }

        /* Bottom padding helper for mobile page containers */
        @media (max-width: 768px) {
          body {
            padding-bottom: 80px !important;
          }
        }
      `;
      document.head.appendChild(style);
    },

    // Inject Mobile Bottom Navigation Bar
    injectMobileNav() {
      if (document.getElementById('sikander-bottom-nav') || document.getElementById('quick-launch-dock')) return;

      const path = window.location.pathname.toLowerCase();
      const isHome = path.endsWith('index.html') || path.endsWith('/') || path === '';
      const isCinema = path.endsWith('cinema.html');
      const isProperty = path.endsWith('property.html');
      const isMusic = path.endsWith('music.html');
      const isCareer = path.endsWith('career.html');
      const isFinance = path.endsWith('finance.html');
      const isHealth = path.endsWith('health.html');

      // If on index.html with its own dock, do not inject
      if (isHome) return;

      const nav = document.createElement('nav');
      nav.id = 'sikander-bottom-nav';
      nav.className = 'sikander-bottom-nav';
      nav.setAttribute('aria-label', 'Sikander OS Mobile Navigation');

      nav.innerHTML = `
        <a href="index.html" class="sikander-nav-item ${isHome ? 'active' : ''}">
          <span class="nav-icon">⚡</span>
          <span>Home</span>
        </a>
        <a href="cinema.html" class="sikander-nav-item ${isCinema ? 'active' : ''}">
          <span class="nav-icon">🎬</span>
          <span>Cinema</span>
        </a>
        <a href="finance.html#property" class="sikander-nav-item ${isProperty ? 'active' : ''}">
          <span class="nav-icon">🏢</span>
          <span>Property</span>
        </a>
        <a href="music.html" class="sikander-nav-item ${isMusic ? 'active' : ''}">
          <span class="nav-icon">🎵</span>
          <span>Music</span>
        </a>
        <a href="career.html" class="sikander-nav-item ${isCareer ? 'active' : ''}">
          <span class="nav-icon">💼</span>
          <span>Career</span>
        </a>
        <a href="finance.html" class="sikander-nav-item ${isFinance && !isProperty ? 'active' : ''}">
          <span class="nav-icon">🏦</span>
          <span>Finance</span>
        </a>
        <a href="health.html" class="sikander-nav-item ${isHealth ? 'active' : ''}">
          <span class="nav-icon">🏃</span>
          <span>Health</span>
        </a>
        <button type="button" class="sikander-nav-item" onclick="window.SikanderSync.openSyncModal()">
          <span class="nav-icon">🔄</span>
          <span>Sync</span>
        </button>
      `;

      document.body.appendChild(nav);
    },

    // Inject Install Banner & Sync Modal & Toast
    injectSyncModal() {
      // 1. Install Banner
      if (!document.getElementById('sikander-install-banner')) {
        const banner = document.createElement('div');
        banner.id = 'sikander-install-banner';
        banner.className = 'sikander-install-banner';
        banner.innerHTML = `
          <div class="install-banner-left">
            <div class="install-gem">⚡</div>
            <div class="install-texts">
              <h4>Install Sikander OS</h4>
              <p>Install standalone native app for offline life cockpit</p>
            </div>
          </div>
          <div class="install-banner-actions">
            <button class="btn-install-trigger" onclick="window.SikanderSync.promptInstall()">Install</button>
            <button class="btn-install-dismiss" onclick="window.SikanderSync.dismissInstallBanner()" title="Dismiss">✕</button>
          </div>
        `;
        document.body.appendChild(banner);
      }

      // 2. Sync Modal
      if (!document.getElementById('sikander-sync-modal')) {
        const modal = document.createElement('div');
        modal.id = 'sikander-sync-modal';
        modal.className = 'sikander-sync-modal-backdrop';
        modal.innerHTML = `
          <div class="sikander-sync-modal-box">
            <div class="sync-modal-header">
              <div class="sync-modal-title">
                <span>🔄</span> Multi-Device Sync & Storage Core
              </div>
              <button class="btn-install-dismiss" onclick="window.SikanderSync.closeSyncModal()">✕</button>
            </div>

            <div class="sync-stat-strip" id="sync-stats-container">
              <!-- Dynamically populated -->
            </div>

            <div style="margin-bottom: 18px;">
              <button class="sync-action-btn btn-export-sync" onclick="window.SikanderSync.exportSnapshot()">
                <span>📦</span> 1-Click Export Data Snapshot (.json)
              </button>
              
              <button class="sync-action-btn btn-import-sync" onclick="document.getElementById('sync-file-input').click()">
                <span>📥</span> 1-Click Import Data Snapshot (.json)
              </button>
              <input type="file" id="sync-file-input" accept=".json" style="display: none;" onchange="window.SikanderSync.handleFileImport(event)">
            </div>

            <div class="sync-guide-box">
              <h5>🌐 Multi-Device Sync Bridge (Home PC ↔ Work PC ↔ Mobile)</h5>
              <p>
                <strong>Method 1 (Instant File Transfer)</strong>: Click <em>Export Data Snapshot</em> on your current device, send the small JSON file via WhatsApp or Drive, and tap <em>Import</em> on your other device.<br>
                <strong>Method 2 (GitHub Repository Bridge)</strong>: Edits saved to <code>data/sikander_unified_data.json</code> can be committed & pushed to GitHub. GitHub Pages deploys updates automatically across all connected PCs and phones.<br>
                <strong>Method 3 (PWA Offline Isolation)</strong>: Even without WiFi or 4G, all changes are saved locally to IndexedDB & LocalStorage and retained permanently.
              </p>
            </div>

            <div style="margin-top: 14px; text-align: right;">
              <button style="background: none; border: none; color: #64748b; font-size: 11px; cursor: pointer; text-decoration: underline;" onclick="window.SikanderSync.resetStorage()">
                Reset / Purge Local Cache
              </button>
            </div>
          </div>
        `;
        document.body.appendChild(modal);
      }

      // 3. Toast
      if (!document.getElementById('sikander-toast')) {
        const toast = document.createElement('div');
        toast.id = 'sikander-toast';
        toast.className = 'sikander-toast';
        document.body.appendChild(toast);
      }
    },

    // Handle file input for import
    handleFileImport(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        this.importSnapshot(e.target.result, 'merge');
      };
      reader.readAsText(file);
      event.target.value = '';
    },

    // Show temporary toast message
    showToast(message, duration = 3000) {
      const toast = document.getElementById('sikander-toast');
      if (toast) {
        toast.textContent = message;
        toast.style.display = 'block';
        clearTimeout(toast._timeout);
        toast._timeout = setTimeout(() => {
          toast.style.display = 'none';
        }, duration);
      }
    },

    // Reset storage with confirmation
    resetStorage() {
      if (confirm('Are you sure you want to reset your local data cache? (A backup export will be generated first)')) {
        this.exportSnapshot();
        const devId = localStorage.getItem('sikander_device_id');
        localStorage.clear();
        if (devId) localStorage.setItem('sikander_device_id', devId);
        this.showToast('Local cache reset. Reloading...');
        setTimeout(() => window.location.reload(), 1000);
      }
    }
  };

  // Expose to window
  window.SikanderSync = SikanderSync;

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SikanderSync.init());
  } else {
    SikanderSync.init();
  }

})(window, document);
