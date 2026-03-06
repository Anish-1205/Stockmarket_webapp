import './globals.css';

export const metadata = {
  title: 'Signal Trader - Mean Reversion Trading Signals',
  description: 'Real-time mean reversion signals for NSE stocks',
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-900">{children}</body>
    </html>
  );
}