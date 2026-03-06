import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MeanReversionStrategy:
    """Mean Reversion strategy - NO PANDAS"""
    
    def __init__(self):
        self.name = "Mean Reversion"
    
    def fetch_data(self, ticker: str, days: int = 730):
        """Fetch data using yfinance"""
        try:
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=days)
            
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                raise ValueError(f"No data for {ticker}")
            
            # Convert to dict of lists - use item() for numpy scalars
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
            
            years = []
            for d in data.index:
                years.append(int(d.year))
            
            result = {
                'dates': [str(d.date()) for d in data.index],
                'opens': opens,
                'closes': closes,
                'years': years
            }
            
            return result
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
    
    def calculate_metrics(self, data):
        """Calculate all metrics - pure Python"""
        opens = data['opens']
        closes = data['closes']
        years = data['years']
        
        # Daily changes
        daily_changes = []
        for i in range(len(opens)):
            change = ((closes[i] - opens[i]) / opens[i]) * 100
            daily_changes.append(change)
        
        # Gaps
        gaps = [0.0]  # First gap is 0
        for i in range(1, len(opens)):
            gap = ((opens[i] - closes[i-1]) / closes[i-1]) * 100
            gaps.append(gap)
        
        # Stresses
        stresses = [0.0]  # First stress is 0
        for i in range(1, len(daily_changes)):
            stress = daily_changes[i-1] + gaps[i]
            stresses.append(stress)
        
        return {
            'opens': opens,
            'closes': closes,
            'daily_changes': daily_changes,
            'gaps': gaps,
            'stresses': stresses,
            'years': years
        }
    
    def get_signal(self, changes, stress_value):
        """Generate signal from changes and stress"""
        if len(changes) < 2:
            return "HOLD", 0.0, 0.0, 0.0
        
        # Get gains and losses
        gains = [x for x in changes if x > 0]
        losses = [x for x in changes if x < 0]
        
        if not gains:
            avg_gain = 0.5
        else:
            avg_gain = sum(gains) / len(gains)
        
        if not losses:
            avg_loss = -0.5
        else:
            avg_loss = sum(losses) / len(losses)
        
        # Decision logic
        if stress_value < avg_loss:
            signal = "BUY"
            pred = abs(avg_loss) * 0.5
        elif stress_value > avg_gain:
            signal = "SELL"
            pred = -(avg_gain * 0.5)
        else:
            signal = "HOLD"
            pred = 0.0
        
        return signal, pred, avg_gain, avg_loss
    
    def backtest_year(self, data, year_to_test):
        """Backtest for a specific year"""
        opens = data['opens']
        closes = data['closes']
        stresses = data['stresses']
        daily_changes = data['daily_changes']
        years = data['years']
        
        # Get indices for this year
        indices = [i for i in range(len(years)) if years[i] == year_to_test]
        
        if len(indices) < 3:
            return {'trades': 0, 'wins': 0, 'win_rate': 0.0, 'total_pnl': 0.0}
        
        trades = 0
        wins = 0
        total_pnl = 0.0
        
        # Backtest
        for idx in indices[2:]:
            try:
                # Historical changes up to this point
                hist_changes = [daily_changes[i] for i in indices if i < idx]
                
                if len(hist_changes) < 2:
                    continue
                
                stress = stresses[idx]
                sig, pred, avg_g, avg_l = self.get_signal(hist_changes, stress)
                
                if sig != "HOLD":
                    open_price = opens[idx]
                    close_price = closes[idx]
                    
                    if sig == "BUY":
                        pnl = ((close_price - open_price) / open_price) * 100
                    else:
                        pnl = ((open_price - close_price) / open_price) * 100
                    
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
        
        # Yesterday's metrics
        yesterday_close = data['closes'][-1]
        yesterday_change = data['daily_changes'][-1]
        
        # Today's gap and stress
        today_gap = ((today_opening_price - yesterday_close) / yesterday_close) * 100
        today_stress = yesterday_change + today_gap
        
        # Get signal
        sig, pred, avg_g, avg_l = self.get_signal(data['daily_changes'], today_stress)
        
        # Backtests
        year1 = self.backtest_year(data, 2024)
        year2 = self.backtest_year(data, 2025)
        
        # Predicted close
        pred_close = today_opening_price * (1 + pred / 100)
        confidence = year2['win_rate'] if year2['trades'] > 0 else 50.0
        
        return {
            'signal': sig,
            'confidence': confidence,
            'predicted_move': pred,
            'predicted_close': pred_close,
            'avg_gain': avg_g,
            'avg_loss': avg_l,
            'combined_stress': today_stress,
            'yesterday_close': yesterday_close,
            'yesterday_change': yesterday_change,
            'today_gap': today_gap,
            'year1_win_rate': year1['win_rate'],
            'year2_win_rate': year2['win_rate'],
            'year1_pnl': year1['total_pnl'],
            'year2_pnl': year2['total_pnl'],
            'year1_trades': year1['trades'],
            'year2_trades': year2['trades'],
        }