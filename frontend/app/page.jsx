'use client';

import React, { useState, useEffect } from 'react';
import { signalAPI } from '../lib/api';

export default function Dashboard() {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [openingPrice, setOpeningPrice] = useState('');
  const [strategy, setStrategy] = useState('mean_reversion');
  const [loading, setLoading] = useState(false);
  const [signal, setSignal] = useState(null);
  const [error, setError] = useState(null);
  const [apiHealthy, setApiHealthy] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await signalAPI.healthCheck();
        setApiHealthy(true);
      } catch (err) {
        setApiHealthy(false);
      }
    };
    checkHealth();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!ticker.trim()) {
      setError('Please enter a ticker');
      return;
    }
    if (!openingPrice || isNaN(openingPrice) || parseFloat(openingPrice) <= 0) {
      setError('Please enter a valid opening price');
      return;
    }

    setLoading(true);

    try {
      let result;
      if (strategy === 'mean_reversion') {
        result = await signalAPI.getMeanReversionSignal(
          ticker.trim().toUpperCase(),
          parseFloat(openingPrice)
        );
      } else if (strategy === 'momentum') {
        result = await signalAPI.getMomentumSignal(
          ticker.trim().toUpperCase(),
          parseFloat(openingPrice)
        );
      } else if (strategy === 'intraday_mean_reversion') {
        result = await signalAPI.getIntradaySignal(
          ticker.trim().toUpperCase(),
          parseFloat(openingPrice)
        );
      }
      setSignal(result);
    } catch (err) {
      setError(err.message);
      setSignal(null);
    } finally {
      setLoading(false);
    }
  };

  const getSignalColor = (signalType) => {
    switch (signalType) {
      case 'BUY':
        return 'from-green-500 to-emerald-600';
      case 'SELL':
        return 'from-red-500 to-rose-600';
      case 'HOLD':
        return 'from-amber-500 to-orange-600';
      default:
        return 'from-gray-500 to-slate-600';
    }
  };

  const getSignalIcon = (signalType) => {
    switch (signalType) {
      case 'BUY':
        return '📈';
      case 'SELL':
        return '📉';
      case 'HOLD':
        return '⏸️';
      default:
        return '❓';
    }
  };

  const getStrategyName = (strategyKey) => {
    if (strategyKey === 'mean_reversion') return 'Mean Reversion';
    if (strategyKey === 'momentum') return 'Momentum';
    if (strategyKey === 'intraday_mean_reversion') return 'Intraday Mean Reversion';
    return strategyKey;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-5"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-5"></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="text-4xl">⚡</div>
            <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Signal Trader
            </h1>
          </div>
          <p className="text-slate-400 text-lg">Real-time trading signals for NSE stocks</p>
        </div>

        <div className="mb-8">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg w-fit mx-auto ${
            apiHealthy 
              ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
              : 'bg-red-500/10 text-red-400 border border-red-500/20'
          }`}>
            <div className={`w-2 h-2 rounded-full ${apiHealthy ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm font-medium">
              {apiHealthy ? 'Backend Connected' : 'Backend Disconnected'}
            </span>
          </div>
        </div>

        <div className="bg-gradient-to-b from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="mb-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-6">
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">
                  Strategy
                </label>
                <select
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
                  disabled={loading}
                >
                  <option value="mean_reversion">Mean Reversion</option>
                  <option value="momentum">Momentum</option>
                  <option value="intraday_mean_reversion">Intraday Mean Reversion</option>
                </select>
                <p className="text-xs text-slate-400 mt-2">Choose trading strategy</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">
                  Stock Ticker
                </label>
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  placeholder="e.g., RELIANCE.NS"
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
                  disabled={loading}
                />
                <p className="text-xs text-slate-400 mt-2">Use .NS for NSE stocks</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">
                  Today's Opening Price (₹)
                </label>
                <input
                  type="number"
                  value={openingPrice}
                  onChange={(e) => setOpeningPrice(e.target.value)}
                  placeholder="e.g., 2850.50"
                  step="0.01"
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
                  disabled={loading}
                />
                <p className="text-xs text-slate-400 mt-2">Today's market opening price</p>
              </div>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm font-medium">⚠️ {error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !apiHealthy}
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-slate-600 disabled:to-slate-700 text-white font-semibold rounded-lg transition transform hover:scale-105 disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <span>🔍</span>
                  Generate Signal
                </>
              )}
            </button>
          </form>

          {signal && (
            <div>
              <div className={`bg-gradient-to-r ${getSignalColor(signal.signal)} rounded-xl p-8 mb-8 text-white shadow-2xl`}>
                <div className="text-center">
                  <div className="text-6xl mb-4">{getSignalIcon(signal.signal)}</div>
                  <h2 className="text-5xl font-bold mb-2">{signal.signal}</h2>
                  <p className="text-xl opacity-90">Confidence: {signal.confidence.toFixed(1)}%</p>
                  <p className="text-sm opacity-75 mt-2">Strategy: {getStrategyName(strategy)}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
                <div className="bg-slate-700/30 border border-slate-600/30 rounded-lg p-4">
                  <p className="text-slate-400 text-sm font-medium mb-1">Predicted Move</p>
                  <p className={`text-2xl font-bold ${signal.predicted_move_percent > 0 ? 'text-green-400' : signal.predicted_move_percent < 0 ? 'text-red-400' : 'text-slate-300'}`}>
                    {signal.predicted_move_percent > 0 ? '+' : ''}{signal.predicted_move_percent.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-slate-700/30 border border-slate-600/30 rounded-lg p-4">
                  <p className="text-slate-400 text-sm font-medium mb-1">Predicted Close</p>
                  <p className="text-2xl font-bold text-cyan-400">
                    ₹{signal.predicted_close_price.toFixed(2)}
                  </p>
                </div>

                <div className="bg-slate-700/30 border border-slate-600/30 rounded-lg p-4">
                  <p className="text-slate-400 text-sm font-medium mb-1">Combined Stress</p>
                  <p className={`text-2xl font-bold ${Math.abs(signal.combined_stress) > 2 ? 'text-orange-400' : 'text-slate-300'}`}>
                    {signal.combined_stress > 0 ? '+' : ''}{signal.combined_stress.toFixed(2)}%
                  </p>
                </div>

                <div className="bg-slate-700/30 border border-slate-600/30 rounded-lg p-4">
                  <p className="text-slate-400 text-sm font-medium mb-2">Historical Accuracy</p>
                  <div className="space-y-1">
                    <p className="text-sm">
                      <span className="text-slate-400">2024: </span>
                      <span className="text-green-400 font-semibold">{signal.year1_win_rate.toFixed(1)}%</span>
                    </p>
                    <p className="text-sm">
                      <span className="text-slate-400">2025: </span>
                      <span className="text-green-400 font-semibold">{signal.year2_win_rate.toFixed(1)}%</span>
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-700/20 border border-slate-600/30 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-slate-200 mb-4">📊 Detailed Analysis</h3>
                
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
                  <div>
                    <p className="text-slate-400 text-xs uppercase tracking-wider">Avg Gain Day</p>
                    <p className="text-lg font-bold text-green-400">{signal.avg_gain_day.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-xs uppercase tracking-wider">Avg Loss Day</p>
                    <p className="text-lg font-bold text-red-400">{signal.avg_loss_day.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-xs uppercase tracking-wider">Yesterday Gap</p>
                    <p className="text-lg font-bold text-slate-300">
                      {signal.analysis_details.today_gap > 0 ? '+' : ''}{signal.analysis_details.today_gap.toFixed(2)}%
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-600/30">
                  <p className="text-slate-400 text-sm">
                    <span className="font-semibold">Year 2025 Performance:</span> {signal.year2_trades} trades, {signal.year2_total_pnl.toFixed(2)}% total P&L
                  </p>
                </div>
              </div>

              <div className="mt-8 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <p className="text-blue-300 text-sm leading-relaxed">
                  💡 <span className="font-semibold">Strategy:</span> This signal is based on {getStrategyName(strategy)} analysis. Use it as one input among other factors for trading decisions.
                </p>
              </div>
            </div>
          )}

          {!signal && !loading && (
            <div className="text-center py-12">
              <div className="text-5xl mb-4">📈</div>
              <p className="text-slate-400">Select a strategy, enter a ticker and opening price to generate a signal</p>
            </div>
          )}
        </div>

        <div className="text-center mt-12 text-slate-500 text-sm">
          <p>Signal Trader v1.0 • Data from Yahoo Finance</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}