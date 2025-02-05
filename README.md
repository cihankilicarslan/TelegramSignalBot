Crypto Signal Bot (app.py)
This bot is designed to analyze cryptocurrency market data and send trading signals via Telegram. It uses technical indicators like RSI, MACD, support/resistance levels, and large trade detection to provide insights into potential buy/sell opportunities.

Features
Real-time Market Analysis: Fetches live market data from Binance for selected cryptocurrency pairs.
Technical Indicators:
RSI (Relative Strength Index): Detects overbought/oversold conditions.
MACD (Moving Average Convergence Divergence): Identifies trend direction and momentum.

Support & Resistance Levels: Calculates key price levels for each pair.
Large Trade Detection: Monitors trades on Binance and alerts if a trade exceeds $100,000 in value.

Telegram Integration: Sends automated signals to a Telegram chat at regular intervals.
Customizable Pairs: Supports multiple cryptocurrency pairs (e.g., BTC/USDT, ETH/USDT).
Prerequisites
Before running the bot, ensure you have the following:

Python 3.8+ installed on your system.
Install the required Python libraries:

pip install ccxt pandas pandas-ta python-telegram-bot asyncio
A Telegram Bot Token :

Create a bot using the BotFather on Telegram.
Replace YourTelegramToken in the code with your bot's token.
A Telegram Chat ID :

Start a conversation with your bot and retrieve the chat ID using a tool like GetChatID .
Replace YourChatID in the code with your chat ID.
How It Works
Market Data Fetching:

The bot fetches OHLCV (Open, High, Low, Close, Volume) data for the specified cryptocurrency pairs from Binance.
It uses the ccxt library to interact with the Binance API.
Technical Analysis:
The bot calculates technical indicators like RSI and MACD using the pandas_ta library.
Support and resistance levels are determined based on historical price data.

Signal Generation:
Buy/sell signals are generated based on RSI and MACD conditions:
Buy Signal: RSI < 30 (oversold) and MACD > 0.
Sell Signal: RSI > 70 (overbought) and MACD < 0.
Entry points, targets, and stop-loss levels are calculated for each signal.

Large Trade Detection:
The bot monitors recent trades on Binance and alerts if a trade exceeds $100,000 in value.

Telegram Notifications:
Signals and alerts are sent to a Telegram chat using the python-telegram-bot library.
Messages include current price, support/resistance levels, RSI, MACD, and trade details.

Scheduled Execution:
The bot runs continuously and sends signals every 15 minutes (900 seconds).
Usage
Clone the repository or copy the code into a Python file (e.g., crypto_signal_bot.py).
Update the following variables in the code:
TELEGRAM_TOKEN: Your Telegram bot token.
YourChatID: Your Telegram chat ID.
crypto_pairs: List of cryptocurrency pairs to analyze.

Run the bot:
python crypto_signal_bot.py
Interact with the bot on Telegram:
Use the /start command to get a welcome message.
Use the /signals command to manually trigger signal generation.
Example Output
The bot sends messages like the following to your Telegram chat:
📊 **Current Market Signals**

SOL/USDT 
Current Price: 22.50
Resistance: 23.00 🔴
Support: 22.00 🟢
RSI: 45.67
MACD Signal: 0.12
Trend: Neutral


BTC/USDT 
Current Price: 27,000.00
Resistance: 27,500.00 🔴
Support: 26,500.00 🟢
RSI: 28.45
MACD Signal: 0.30
Trend: Possible Buy
Entry Point: 27,000.00
Target: 27,810.00
Stop Loss: 26,190.00

⚠️ **Large Trade Detected!**
Pair: BTC/USDT
Type: Buy
Price: 27,000.00 USD
Value: 150,000.00 USD
Time: 2023-10-01 14:30:00
