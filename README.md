# ⚡ Sikander OS

> **Personal Life Operating System & Unified Dashboard**  
> Live Production URL: **[https://ckndr.github.io/sikander-os/](https://ckndr.github.io/sikander-os/)**  
> Cinema Hub Module: **[https://ckndr.github.io/sikander-os/cinema.html](https://ckndr.github.io/sikander-os/cinema.html)**

---

## ◈ Overview

**Sikander OS** is an autonomous, hyper-personalized command center designed to centralize entertainment intelligence, cognitive workflows, health performance metrics, and daily execution.

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
  - Filter chips (True Stories, Sci-Fi, Crime Thriller, Psychological, Documentaries)
  - Full local storage synchronization (`localStorage`) for watch states & personal ratings
  - Export for LLMs: 1-click export of the complete taste vector and ratings for ChatGPT / Claude

---

## 📂 Repository Structure

```
sikander-os/
├── index.html                     # Master OS Dashboard & Module Launcher
├── cinema.html                    # Operational Cinema Hub & Taste Engine
├── data/
│   ├── sikander_unified_data.json # Master 373-title unified database
│   └── SIKANDER_CINEMA_AI_PROFILE.md # Full taste profile & prompt engineering spec
├── README.md                      # Architecture & documentation
└── .gitignore                     # Git ignore rules
```

---

## 🚀 Future Module Roadmap

1. **Module 02: Iron & Bio-Metrics Hub** *(Phase 2)*
   - Progressive overload calculations, hypertrophy volume tracking, macro adherence, recovery metrics.
2. **Module 03: Second Brain & Cognitive Graph** *(Phase 2)*
   - Zettelkasten knowledge vault, atomic mental models, cross-referenced research papers.
3. **Module 04: Habit Loop & Sprint Execution** *(Phase 3)*
   - Timeboxing telemetry, deep-work counters, streak protection, micro-journaling.
4. **Module 05: Capital & Wealth Ledger** *(Phase 3)*
   - Portfolio asset distribution, liquidity runways, cash-flow velocity projections.

---

## 🛠️ Local Development

Clone the repository and open `index.html` in any modern web browser:

```bash
git clone https://github.com/ckndr/sikander-os.git
cd sikander-os
# Open in browser:
# On Windows:
start index.html
# Or start a local server:
python -m http.server 8000
```

---

© 2026 Sikander (`ckndr`). Designed & engineered for personal operational excellence.
