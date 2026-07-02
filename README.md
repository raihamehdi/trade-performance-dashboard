# trade-performance-dashboard
A professional-grade **trading journal system built with Django** that helps traders track setups, analyze performance, and refine strategies using structured data and behavioral insights.

This project transforms trading from guesswork into a **data-driven decision system**.

---

## Features

### Trade Journal
- Log every trade setup with structured fields
- Track pair, timeframe, grade, outcome, and RR
- Upload supporting screenshots
- Sequential setup numbering for clean tracking

### Performance Analytics
- Win rate calculation (overall & filtered)
- A-grade vs non-A-grade performance tracking
- Average Risk-to-Reward (RR)
- Progress tracking toward consistency goals

### Psychology Tracking
- Record emotional/psychological tags per trade
- Identify recurring mistakes in losing trades
- Behavioral pattern detection for self-improvement

### Advanced Analytics Dashboard
Breakdown of performance by:
- Trading session (London, NY, Asia, etc.)
- Timeframe (M1, M5, M15, etc.)
- Setup grade (A/B/C)
- Outcome-based filtering

### Mastery System
- Store structured trading insights (findings)
- Group learnings by category
- Track coin/pair-specific behavior
- Build a personal strategy knowledge base

### Strategy Module (SMC-Based)
Built-in structured strategy documentation system based on **Smart Money Concepts**:

- BOS (Break of Structure)
- CHoCH (Change of Character)
- Liquidity zones
- Strong High / Strong Low identification
- Rule-based entry confirmation system

---

## Tech Stack

- **Backend:** Django (Python)
- **Database:** SQLite (dev) / PostgreSQL (prod-ready)
- **Frontend:** Django Templates (HTML/CSS)
- **Styling:** Bootstrap
- **Auth:** Django Authentication System
- **ORM:** Django ORM (advanced aggregations & filtering)

---

## Core Idea

> “Trading performance improves only when behavior becomes measurable.”

This system focuses on:
- Data-driven journaling
- Emotional accountability
- Structured strategy execution
- Continuous improvement loop

---

## Project Structure


journal/
│
├── views.py # Core logic (dashboard, analytics, mastery, strategy)
├── models.py # Setup, Finding, StrategyNote models
├── forms.py # Django forms for input handling
├── templates/
│ ├── dashboard.html
│ ├── detail.html
│ ├── analytics.html
│ ├── mastery.html
│ └── strategy.html


---

## Analytics Engine

The system uses Django ORM aggregation to compute:

- Win rate across trades
- Session-based performance
- Timeframe effectiveness
- Grade-wise performance scoring
- Psychological loss pattern analysis

---

## Strategy Framework (SMC Model)

Core trading logic implemented in strategy module:

- **BOS:** Continuation confirmation after liquidity sweep  
- **CHoCH:** Potential reversal signal  
- **Strong High/Low Zones:** Institutional order regions  
- **Entry Rule:** Candle must close back outside zone for confirmation  
- **Risk Logic:** Structured stop-loss beyond liquidity zones  

---

## Future Improvements

- Broker API integration for auto trade logging
- Chart visualization (TradingView-style overlays)
- AI-based trade review assistant
- Equity curve tracking
- Real-time setup alerts
- Mobile PWA version

---

## Setup Instructions

```bash
git clone https://github.com/your-username/trading-journal.git
cd trading-journal

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

python manage.py migrate
python manage.py runserver
