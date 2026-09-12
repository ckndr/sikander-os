# ⚡ Sikander OS

> **Personal Life Operating System & Unified Dashboard**  
> Live Production URL: **[https://ckndr.github.io/sikander-os/](https://ckndr.github.io/sikander-os/)**  
> Cinema Hub Module: **[https://ckndr.github.io/sikander-os/cinema.html](https://ckndr.github.io/sikander-os/cinema.html)**  
> Real Estate & Property Ledger: **[https://ckndr.github.io/sikander-os/property.html](https://ckndr.github.io/sikander-os/property.html)**

---

## ◈ Overview

**Sikander OS** is an autonomous, hyper-personalized command center designed to centralize entertainment intelligence, cognitive workflows, real estate assets, health performance metrics, and daily execution.

The architecture is built on pure, high-performance web standards (HTML5, modern CSS3, native ECMAScript) with zero external frameworks or server overhead, deployed continuously via **GitHub Pages**.

---

## 🎬 Module 01: Cinema Hub & Taste Engine (LIVE)

The first operational module in Sikander OS is the **Cinema Hub** — an algorithmic film and series recommendation engine trained on Sikander's IMDb rating history and Instagram saved archive.

### Key Capabilities:
- **373 Fully Enriched Titles**:
  - **217 Watchlist items** (188 Feature Films, 17 TV/Mini-Series, 12 Curated Recs)
  - **156 Watched history items** with original ratings and review timestamps
  - **56 Ingested items** directly scraped & enriched from Sikander's live Instagram saved reels collection
- **6-Pillar Taste Vector Engine**:
  1. *Dark / Cynical Realism* (25%)
  2. *Plausible High-Concept Sci-Fi* (20%)
  3. *Psychological Tension & Moral Ambiguity* (20%)
  4. *High-Agency Protagonists* (15%)
  5. *Airtight Narrative Architecture* (10%)
  6. *Visual & Atmospheric Distinctiveness* (10%)
- **Interactive Features**:
  - Direct embedded YouTube Trailers
  - 1-Click title copy button with toast feedback
  - Multi-directional sorting (Taste Match %, IMDb Rating, Release Year, A-Z)
  - Country origin flags and native language badges
  - Compact Power-User Table View vs. Cinematic Poster Grid View
  - Full local storage synchronization (`localStorage`) for watch states & personal ratings

---

## 🏢 Module 02: Real Estate & Property Ledger (LIVE)

The second operational module in Sikander OS is the **Property Ledger** — a complete financial intelligence portal for real estate capital outlays, mortgage/loan facilities, utility infrastructure installations, and official receipt verification.

### Target Asset:
- **Project**: Al Ghafoor Towers & Mall (Sector 12, Surjani Town, Karachi)
- **Unit**: Unit 206 (Apartments / Residential) | File No: `ATM-14A-206-2` (Utility Ref: `ATM-14A-206-1`)
- **Allottee**: Muhammad Sikander

### Financial Overview:
- **Total Capital Outlay**: **PKR 3,124,000**
  - Flat Purchase Cost: PKR 2,174,000 (Schedule: 1,449,000 + Loan: 725,000)
  - Net Utility Installation Charges: PKR 950,000 (After approved Rs. 250k discount from 1.2M demand)
- **Cumulative Paid to Date**: **PKR 2,093,000** (**67.0% equity / settled**)
- **Remaining Liability**: **PKR 1,031,000** (Flat loan: 216k + Utilities: 815k)
- **Next Milestone**: **Month 10 (Sep 2026) · PKR 15,000**

### Key Capabilities:
- **37-Month Utility Timeline**: Interactive schedule with status badges (`PAID`, `NEXT DUE`, `SCHEDULED`), Raast transaction IDs, official DC receipt numbers, and 1-click receipt previews.
- **100-Transaction Historical Flat Ledger**: Complete audit trail of all payments from booking in April 2022 to September 2025 across all construction milestones and loan repayments.
- **Interactive Document Vault (20 Verified Archives)**: Full lightbox viewer for official Delivery Counter receipts, bank transfer slips (Habib Metro Raast), legal undertaking, payment plans, and official client ledger PDF.
- **Privacy Mode Toggle**: 1-click toggle to mask sensitive PII (CNIC, phone number, address, file number) for clean sharing and public safety.
- **Multi-Year Cash Flow Analytics**: Year-by-year cash outflow schedule to plan liquidity for 2026, 2027, and 2028.

---

## 📂 Repository Structure

```
sikander-os/
├── index.html                     # Master OS Dashboard & Module Launcher
├── cinema.html                    # Operational Module 01: Cinema Hub & Taste Engine
├── property.html                  # Operational Module 02: Real Estate & Property Ledger
├── data/
│   ├── sikander_unified_data.json # Master 373-title unified cinema database
│   ├── SIKANDER_CINEMA_AI_PROFILE.md # Cinema taste profile & prompt engineering spec
│   └── property/
│       ├── alghafoor_property_ledger.json # Master property financial database
│       └── receipts/              # Verified archive of all 20 receipt images & PDF
├── README.md                      # Architecture & documentation
└── .gitignore                     # Git ignore rules
```

---

## 🚀 Future Module Roadmap

1. **Module 03: Iron & Bio-Metrics Hub** *(Phase 2)*
   - Progressive overload calculations, hypertrophy volume tracking, macro adherence, recovery metrics.
2. **Module 04: Second Brain & Cognitive Graph** *(Phase 2)*
   - Zettelkasten knowledge vault, atomic mental models, cross-referenced research papers.
3. **Module 05: Habit Loop & Sprint Execution** *(Phase 3)*
   - Timeboxing telemetry, deep-work counters, streak protection, micro-journaling.
4. **Module 06: Capital & Wealth Ledger** *(Phase 3)*
   - Portfolio asset distribution, liquidity runways, cash-flow velocity projections.

---

## 🛠️ Local Development & Usage

Clone or navigate to the local repository on `I:\sikander-os`:

```bash
# On Windows:
cd I:\sikander-os
start index.html
# Or start a local server:
python -m http.server 8000
```

---

© 2026 Sikander (`ckndr`). Designed & engineered for personal operational excellence.
