import asyncio
import ccxt
import pandas as pd
import pandas_ta as ta
import telegram
from telegram.ext import Application, CommandHandler

# Binance connection (for crypto data)
exchange = ccxt.binance()

# Telegram bot token
TELEGRAM_TOKEN = 'YourTelegramToken'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Crypto pair list
crypto_pairs = ['SOL/USDT', 'BCH/USDT', 'LTC/USDT', 'ETH/USDT', 'BTC/USDT']

# Signal sending function
async def send_signals():
    message = "📊 **Current Market Signals**\n\n"
    for pair in crypto_pairs:
        # Fetch price data
        df = fetch_market_data(pair)
        if df is None:
            continue
        
        current_price = df['close'].iloc[-1]
        # Detect support and resistance levels
        support, resistance = calculate_support_resistance(df)
        
        # Calculate technical analysis data
        rsi, macd_signal, direction = technical_analysis(df)
        
        # Trend and signal analysis
        trend_signal, target, stop_loss, entry_point = determine_trend(rsi, macd_signal, pair)
        
        # Large buy or sell transaction check
        large_trade_signal = None
    
        try:
            # Fetch trades from Binance
            trades = exchange.fetch_trades(pair)
            # Check the last 100 trades (you can increase the number as needed)
            for trade in trades[:5000]:  # Fetch the last 1000 trades
                trade_value = trade['price'] * trade['amount']
                
                # If the trade value is greater than $100,000, check whether it's a buy or sell
                if trade_value > 100000:  # Trades larger than $100,000
                    trade_type = "Buy" if trade['side'] == 'buy' else "Sell"
                    # Convert time information
                    trade_time = pd.to_datetime(trade['timestamp'], unit='ms').strftime('%Y-%m-%d %H:%M:%S')
                    # Price at which it was sold
                    sold_price = trade['price']
                    large_trade_signal = f"⚠️ **Large Trade Detected!**\nPair: {pair}\nType: {trade_type}\nPrice: {sold_price:.2f} USD\nValue: {trade_value:.2f} USD\nTime: {trade_time}"
                    break  # Exit the loop after detecting the first large trade
        
        except Exception as e:
            print(f"Error fetching trades for {pair}: {e}")
        
        # Build the message
        message += f"{pair} \nCurrent Price: {current_price:.2f}\nResistance: {resistance:.2f} 🔴\nSupport:       {support:.2f} 🟢\nRSI: {rsi:.2f}\nMACD Signal: {macd_signal:.2f}\nTrend: {trend_signal}\n\n"
        if trend_signal != "Neutral":
            message += f"Entry Point: {entry_point}\nTarget: {target}\nStop Loss: {stop_loss}\n\n"
        else:
            message += "\n\n"
        
        # If there is a large buy/sell transaction, include it in the message
        if large_trade_signal:
            message += f"{large_trade_signal}\n\n"
    # Send signals to Telegram    
    await bot.send_message(chat_id='YourChatID', text=message, parse_mode="Markdown")
   #await bot.send_message(chat_id='SecondYourChatID', text=message, parse_mode="Markdown")

# Fetch crypto data and analyze
def fetch_market_data(pair):
    try:
        # Fetch data from Binance
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching data for {pair}: {e}")
        return None

# Calculate support and resistance levels
def calculate_support_resistance(df):
    support = df['low'].min()
    resistance = df['high'].max()
    return support, resistance

# Calculate technical analysis (RSI, MACD)
def technical_analysis(df):
    rsi = ta.rsi(df['close'], length=14).iloc[-1]
    macd = ta.macd(df['close'])
    macd_signal = macd['MACDs_12_26_9'].iloc[-1]
    
    # Determine direction (using RSI and MACD)
    direction = "Neutral"
    if rsi > 70:
        direction = "Overbought"
    elif rsi < 30:
        direction = "Oversold"
    
    return rsi, macd_signal, direction

# Determine overall trend
def determine_trend(rsi, macd_signal, pair):
    trend_signal = "Neutral"
    entry_point = target = stop_loss = None
    
    # Buy signal (Oversold + MACD buy signal)
    if rsi < 30 and macd_signal > 0:
        trend_signal = "Possible Buy"
        entry_point = fetch_market_data(pair)['close'].iloc[-1]  # Current price
        target = entry_point * 1.03  # 3% target
        stop_loss = entry_point * 0.97  # 3% stop
    # Sell signal (Overbought + MACD sell signal)
    elif rsi > 70 and macd_signal < 0:
        trend_signal = "Possible Sell"
        entry_point = fetch_market_data(pair)['close'].iloc[-1]  # Current price
        target = entry_point * 0.97  # 3% target
        stop_loss = entry_point * 1.03  # 3% stop
    
    return trend_signal, target, stop_loss, entry_point

# Telegram commands
async def start(update, context):
    await update.message.reply_text("Hello! This bot sends cryptocurrency price signals. Available commands: /signals")

async def manual_send_signals(update, context):
    await send_signals()

# Send signals every minute
async def scheduled_task():
    while True:
        await send_signals()  # Send signals
        print("Message sent to Telegram.")
        await asyncio.sleep(301)  # Wait for 5 minutes
      
# Run the bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signals", manual_send_signals))
    # Send signals asynchronously
    asyncio.run(scheduled_task())  # Start the event loop
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
