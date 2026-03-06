import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MomentumStrategy:
    """Momentum strategy - trend following"""
    
    def __init__(self):
        self.name = "Momentum"
    
    def fetch_data(self, ticker: str, days: int = 730):
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
        """Calculate momentum metrics"""
        opens = data['opens']
        closes = data['closes']
        years = data['years']
        
        # Calculate returns
        returns = []
        for i in range(len(closes)):
            ret = ((closes[i] - opens[i]) / opens[i]) * 100
            returns.append(ret)
        
        # Calculate momentum (20-day)
        momentum = [0.0] * 20  # First 20 are 0
        for i in range(20, len(closes)):
            mom = ((closes[i] - closes[i-20]) / closes[i-20]) * 100
            momentum.append(mom)
        
        return {
            'opens': opens,
            'closes': closes,
            'returns': returns,
            'momentum': momentum,
            'years': years
        }
    
    def get_signal(self, momentum_value, recent_momentum):
        """Generate signal based on momentum"""
        if len(recent_momentum) < 5:
            return "HOLD", 0.0, 0.0, 0.0
        
        # Average recent momentum
        avg_momentum = sum(recent_momentum[-5:]) / 5
        
        # Positive momentum = uptrend
        if momentum_value > 2.0:
            signal = "BUY"
            pred = 0.5  # Expect small gain
        elif momentum_value < -2.0:
            signal = "SELL"
            pred = -0.5  # Expect small loss
        else:
            signal = "HOLD"
            pred = 0.0
        
        return signal, pred, avg_momentum, momentum_value
    
    def backtest_year(self, data, year_to_test):
        """Backtest for a specific year"""
        opens = data['opens']
        closes = data['closes']
        momentum = data['momentum']
        years = data['years']
        
        # Get indices for this year
        indices = [i for i in range(len(years)) if years[i] == year_to_test]
        
        if len(indices) < 25:
            return {'trades': 0, 'wins': 0, 'win_rate': 0.0, 'total_pnl': 0.0}
        
        trades = 0
        wins = 0
        total_pnl = 0.0
        
        # Backtest
        for idx in indices[20:]:
            try:
                mom = momentum[idx]
                recent_mom = [momentum[i] for i in indices if i < idx][-5:]
                
                sig, pred, avg_m, curr_m = self.get_signal(mom, recent_mom)
                
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
        
        # Get momentum
        curr_momentum = data['momentum'][-1]
        recent_momentum = data['momentum'][-10:]
        
        # Get signal
        sig, pred, avg_m, curr_m = self.get_signal(curr_momentum, recent_momentum)
        
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
            'avg_gain': 0.8,
            'avg_loss': -0.8,
            'combined_stress': curr_momentum,
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