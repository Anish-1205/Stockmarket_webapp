# Trading Signals Dashboard

A full-stack web application that generates real-time trading signals for NSE stocks using multiple strategies.

## Features

- **3 Trading Strategies:**
  - Mean Reversion: Detects overbought/oversold conditions
  - Momentum: Trend-following using 20-day momentum
  - Intraday Mean Reversion: Daily range-based mean reversion with RSI confirmation

- **Signal Generation:**
  - Real-time signal analysis (BUY/SELL/HOLD)
  - Confidence percentage based on historical accuracy
  - Predicted price movements
  - Backtesting on 2024-2025 data

- **User-Friendly Dashboard:**
  - Strategy selector dropdown
  - Beautiful UI with Tailwind CSS
  - Detailed analysis metrics
  - Historical performance data

## Tech Stack

### Frontend
- Next.js 14
- React 18
- Tailwind CSS
- Axios

### Backend
- FastAPI
- Python 3.13
- yfinance (data source)
- Pydantic

## Project Structure
```
trading-signals-dashboard/
├── frontend/
│   ├── app/
│   │   ├── page.jsx (Dashboard)
│   │   ├── layout.jsx
│   │   └── globals.css
│   ├── lib/
│   │   └── api.js (API client, currently missing, see Known issue)
│   └── package.json
├── backend/
│   ├── strategies/
│   │   ├── mean_reversion.py
│   │   ├── momentum.py
│   │   └── intraday_mean_reversion.py
│   ├── main.py (FastAPI server)
│   └── requirements.txt
└── README.md
```

## Installation & Setup

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### Known issue

`frontend/app/page.jsx` imports `frontend/lib/api.js`, but that file is not in this repository. The frontend will not build from a fresh clone until it is restored. The backend is not affected.

## Usage

1. Open `http://localhost:3000` in your browser
2. Select a strategy from the dropdown
3. Enter stock ticker (e.g., RELIANCE.NS)
4. Enter today's opening price
5. Click "Generate Signal"
6. View BUY/SELL/HOLD signal with confidence and predictions

## API Endpoints

- `GET /health` - Health check
- `POST /signal/mean-reversion` - Mean reversion signal
- `POST /signal/momentum` - Momentum signal
- `POST /signal/intraday-mean-reversion` - Intraday mean reversion signal
- `GET /strategies` - List available strategies

## Strategies

### Mean Reversion
- Calculates daily stress based on price moves
- Compares to historical averages
- Win Rate: ~54% (2024-2025)

### Momentum
- Uses 20-day momentum calculation
- Trend-following approach
- Win Rate: ~46-54% (2024-2025)

### Intraday Mean Reversion
- Analyzes daily candle (High/Low/Open/Close)
- RSI confirmation filter
- Expected Win Rate: 60-65%

## Future Roadmap

- [ ] Database integration (PostgreSQL)
- [ ] Real broker integration (Zerodha API)
- [ ] Paper trading mode
- [ ] Signal history/logging
- [ ] User authentication
- [ ] Portfolio tracking
- [ ] Risk management features

## Disclaimer

This project is for educational purposes. Do not use for real trading without thorough backtesting.

## Author

Built by Anish (CSE Student)

## License

MIT
