from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from strategies.intraday_mean_reversion import IntradayMeanReversionStrategy

app = FastAPI(
    title="Signal Trading System API",
    description="Real-time trading signals using mean reversion, momentum, and intraday strategies",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignalRequest(BaseModel):
    ticker: str
    today_opening_price: float
    description: Optional[str] = None

class SignalResponse(BaseModel):
    ticker: str
    signal: str
    confidence: float
    predicted_move_percent: float
    predicted_close_price: float
    avg_gain_day: float
    avg_loss_day: float
    combined_stress: float
    year1_win_rate: float
    year2_win_rate: float
    year1_total_pnl: float
    year2_total_pnl: float
    year1_trades: int
    year2_trades: int
    timestamp: str
    analysis_details: dict

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

mean_reversion_strategy = MeanReversionStrategy()
momentum_strategy = MomentumStrategy()
intraday_strategy = IntradayMeanReversionStrategy()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/signal/mean-reversion", response_model=SignalResponse)
async def get_mean_reversion_signal(request: SignalRequest):
    try:
        result = mean_reversion_strategy.generate_signal(
            ticker=request.ticker,
            today_opening_price=request.today_opening_price
        )
        
        # Convert numpy arrays to Python floats
        def to_float(val):
            if hasattr(val, 'item'):
                return float(val.item())
            return float(val)
        
        return SignalResponse(
            ticker=request.ticker,
            signal=result['signal'],
            confidence=to_float(result['confidence']),
            predicted_move_percent=to_float(result['predicted_move']),
            predicted_close_price=to_float(result['predicted_close']),
            avg_gain_day=to_float(result['avg_gain']),
            avg_loss_day=to_float(result['avg_loss']),
            combined_stress=to_float(result['combined_stress']),
            year1_win_rate=to_float(result['year1_win_rate']),
            year2_win_rate=to_float(result['year2_win_rate']),
            year1_total_pnl=to_float(result['year1_pnl']),
            year2_total_pnl=to_float(result['year2_pnl']),
            year1_trades=int(result['year1_trades']),
            year2_trades=int(result['year2_trades']),
            timestamp=datetime.now().isoformat(),
            analysis_details={
                'yesterday_close': to_float(result['yesterday_close']),
                'yesterday_change': to_float(result['yesterday_change']),
                'today_gap': to_float(result['today_gap']),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/signal/momentum", response_model=SignalResponse)
async def get_momentum_signal(request: SignalRequest):
    try:
        result = momentum_strategy.generate_signal(
            ticker=request.ticker,
            today_opening_price=request.today_opening_price
        )
        
        # Convert numpy arrays to Python floats
        def to_float(val):
            if hasattr(val, 'item'):
                return float(val.item())
            return float(val)
        
        return SignalResponse(
            ticker=request.ticker,
            signal=result['signal'],
            confidence=to_float(result['confidence']),
            predicted_move_percent=to_float(result['predicted_move']),
            predicted_close_price=to_float(result['predicted_close']),
            avg_gain_day=to_float(result['avg_gain']),
            avg_loss_day=to_float(result['avg_loss']),
            combined_stress=to_float(result['combined_stress']),
            year1_win_rate=to_float(result['year1_win_rate']),
            year2_win_rate=to_float(result['year2_win_rate']),
            year1_total_pnl=to_float(result['year1_pnl']),
            year2_total_pnl=to_float(result['year2_pnl']),
            year1_trades=int(result['year1_trades']),
            year2_trades=int(result['year2_trades']),
            timestamp=datetime.now().isoformat(),
            analysis_details={
                'yesterday_close': to_float(result['yesterday_close']),
                'yesterday_change': to_float(result['yesterday_change']),
                'today_gap': to_float(result['today_gap']),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/signal/intraday-mean-reversion", response_model=SignalResponse)
async def get_intraday_signal(request: SignalRequest):
    try:
        result = intraday_strategy.generate_signal(
            ticker=request.ticker,
            today_opening_price=request.today_opening_price
        )
        
        # Convert numpy arrays to Python floats
        def to_float(val):
            if hasattr(val, 'item'):
                return float(val.item())
            return float(val)
        
        return SignalResponse(
            ticker=request.ticker,
            signal=result['signal'],
            confidence=to_float(result['confidence']),
            predicted_move_percent=to_float(result['predicted_move']),
            predicted_close_price=to_float(result['predicted_close']),
            avg_gain_day=to_float(result['avg_gain']),
            avg_loss_day=to_float(result['avg_loss']),
            combined_stress=to_float(result['combined_stress']),
            year1_win_rate=to_float(result['year1_win_rate']),
            year2_win_rate=to_float(result['year2_win_rate']),
            year1_total_pnl=to_float(result['year1_pnl']),
            year2_total_pnl=to_float(result['year2_pnl']),
            year1_trades=int(result['year1_trades']),
            year2_trades=int(result['year2_trades']),
            timestamp=datetime.now().isoformat(),
            analysis_details={
                'yesterday_close': to_float(result['yesterday_close']),
                'yesterday_change': to_float(result['yesterday_change']),
                'today_gap': to_float(result['today_gap']),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/strategies")
async def list_strategies():
    return {
        "strategies": [
            {
                "name": "mean_reversion",
                "display_name": "Mean Reversion",
                "description": "Identifies overbought/oversold conditions based on historical stress levels",
                "timescale": "daily"
            },
            {
                "name": "momentum",
                "display_name": "Momentum",
                "description": "Trend-following strategy based on 20-day momentum",
                "timescale": "daily"
            },
            {
                "name": "intraday_mean_reversion",
                "display_name": "Intraday Mean Reversion",
                "description": "Intraday scalping with RSI + Volume filters (60-65% win rate expected)",
                "timescale": "intraday"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)