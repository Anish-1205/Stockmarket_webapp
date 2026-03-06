import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IntradayMeanReversionStrategy:
    """Improved Intraday Mean Reversion Strategy - Fixed for Daily Data"""
    
    def __init__(self):
        self.name = "Intraday Mean Reversion"
    
    def fetch_data(self, ticker: str, days: int = 60):
        """Fetch data using yfinance"""
        try:
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=days)
            
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                raise ValueError(f"No data for {ticker}")
            
            # Convert to dict of lists
            opens = []
            for x in data['Open'].values:
                if hasattr(x, 'item'):
                    opens.append(float(x.item()))
                else:
                    opens.append(float(x))
            
            closes = []
            for x in data['Close'].values:
                if hasattr(x, 'item'):
                    closes.append(float(x.item()))
                else:
                    closes.append(float(x))
            
            highs = []
            for x in data['High'].values:
                if hasattr(x, 'item'):
                    highs.append(float(x.item()))
                else:
                    highs.append(float(x))
            
            lows = []
            for x in data['Low'].values:
                if hasattr(x, 'item'):
                    lows.append(float(x.item()))
                else:
                    lows.append(float(x))
            
            years = []
            for d in data.index:
                years.append(int(d.year))
            
            result = {
                'dates': [str(d.date()) for d in data.index],
                'opens': opens,
                'closes': closes,
                'highs': highs,
                'lows': lows,
                'years': years
            }
            
            return result
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
    
    def calculate_rsi_range(self, closes, start_idx, end_idx, period=14):
        """Calculate RSI for a specific range of closes"""
        if end_idx - start_idx < period:
            return 50.0
        
        relevant_closes = closes[start_idx:end_idx+1]
        
        deltas = []
        for i in range(1, len(relevant_closes)):
            deltas.append(relevant_closes[i] - relevant_closes[i-1])
        
        if not deltas:
            return 50.0
        
        gains = [x for x in deltas if x > 0]
        losses = [abs(x) for x in deltas if x < 0]
        
        avg_gain = sum(gains) / len(gains) if gains else 0.001
        avg_loss = sum(losses) / len(losses) if losses else 0.001
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_metrics(self, data):
        """Calculate all metrics"""
        opens = data['opens']
        closes = data['closes']
        highs = data['highs']
        lows = data['lows']
        years = data['years']
        
        # Daily range
        ranges = []
        for i in range(len(highs)):
            range_pct = ((highs[i] - lows[i]) / lows[i]) * 100
            ranges.append(range_pct)
        
        # Price position in range (0-100)
        positions = []
        for i in range(len(closes)):
            if highs[i] - lows[i] != 0:
                pos = ((closes[i] - lows[i]) / (highs[i] - lows[i])) * 100
            else:
                pos = 50
            positions.append(pos)
        
        # Calculate RSI for current state (last 14 days)
        rsi = self.calculate_rsi_range(closes, max(0, len(closes)-14), len(closes)-1)
        
        return {
            'opens': opens,
            'closes': closes,
            'highs': highs,
            'lows': lows,
            'ranges': ranges,
            'positions': positions,
            'rsi': rsi,
            'years': years
        }
    
    def get_signal(self, data):
        """Generate signal - SIMPLIFIED for daily data"""
        ranges = data['ranges']
        positions = data['positions']
        rsi = data['rsi']
        
        if len(ranges) < 1:
            return "HOLD", 0.0, 0.0
        
        # Current metrics
        current_range = ranges[-1]
        current_position = positions[-1]
        current_rsi = rsi
        
        # Filter: Min Range (0.5% for daily)
        if current_range < 0.5:
            return "HOLD", 0.0, current_range
        
        # Signal Logic
        if current_position < 30 and current_rsi < 45:
            signal = "BUY"
            predicted_move = 0.4
        elif current_position > 70 and current_rsi > 55:
            signal = "SELL"
            predicted_move = -0.4
        else:
            signal = "HOLD"
            predicted_move = 0.0
        
        return signal, predicted_move, current_range
    
    def backtest_year(self, data, year_to_test):
        """Backtest for a specific year"""
        opens = data['opens']
        closes = data['closes']
        highs = data['highs']
        lows = data['lows']
        positions = data['positions']
        ranges = data['ranges']
        years = data['years']
        
        # Get indices for this year
        indices = [i for i in range(len(years)) if years[i] == year_to_test]
        
        if len(indices) < 5:
            return {'trades': 0, 'wins': 0, 'win_rate': 0.0, 'total_pnl': 0.0}
        
        trades = 0
        wins = 0
        total_pnl = 0.0
        
        # Backtest - need at least 14 days before first trade
        for idx in indices:
            try:
                # Need at least 14 days of history
                if idx < 14:
                    continue
                
                # Check range filter
                if ranges[idx] < 0.5:
                    continue
                
                # Calculate RSI up to this point
                rsi = self.calculate_rsi_range(closes, 0, idx)
                
                # Generate signal based on position and RSI
                if positions[idx] < 30 and rsi < 45:
                    sig = "BUY"
                    # Buy at close, sell at next open
                    if idx < len(closes) - 1:
                        pnl = ((opens[idx+1] - closes[idx]) / closes[idx]) * 100
                    else:
                        continue
                elif positions[idx] > 70 and rsi > 55:
                    sig = "SELL"
                    # Short at close, cover at next open
                    if idx < len(closes) - 1:
                        pnl = ((closes[idx] - opens[idx+1]) / closes[idx]) * 100
                    else:
                        continue
                else:
                    continue
                
                trades += 1
                if pnl > 0:
                    wins += 1
                total_pnl += pnl
            except:
                continue
        
        win_rate = (wins / trades * 100) if trades > 0 else 0.0
        
        return {
            'trades': trades,
            'wins': wins,
            'win_rate': win_rate,
            'total_pnl': total_pnl
        }
    
    def generate_signal(self, ticker: str, today_opening_price: float):
        """Main signal generation"""
        # Fetch data
        raw_data = self.fetch_data(ticker)
        data = self.calculate_metrics(raw_data)
        
        # Get signal
        sig, pred, current_range = self.get_signal(data)
        
        # Backtests
        year1 = self.backtest_year(data, 2024)
        year2 = self.backtest_year(data, 2025)
        
        # Predicted close
        pred_close = today_opening_price * (1 + pred / 100)
        confidence = year2['win_rate'] if year2['trades'] > 0 else 50.0
        
        yesterday_close = data['closes'][-1]
        
        return {
            'signal': sig,
            'confidence': confidence,
            'predicted_move': pred,
            'predicted_close': pred_close,
            'avg_gain': 0.4,
            'avg_loss': -0.4,
            'combined_stress': current_range,
            'yesterday_close': yesterday_close,
            'yesterday_change': ((data['closes'][-1] - data['opens'][-1]) / data['opens'][-1]) * 100,
            'today_gap': ((today_opening_price - yesterday_close) / yesterday_close) * 100,
            'year1_win_rate': year1['win_rate'],
            'year2_win_rate': year2['win_rate'],
            'year1_pnl': year1['total_pnl'],
            'year2_pnl': year2['total_pnl'],
            'year1_trades': year1['trades'],
            'year2_trades': year2['trades'],
        }