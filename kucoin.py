import asyncio
import ccxt
import pandas as pd
import ta
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# Kucoin connection (for crypto data)
exchange = ccxt.kucoin()

# Telegram bot settings
TELEGRAM_TOKEN = "YourTelegramToken"
CHAT_ID = "YourChatId"
bot = Bot(token=TELEGRAM_TOKEN)

# Fetch the top 100 USDT pairs by volume
def fetch_top_100_usdt_pairs():
    markets = exchange.load_markets()
    usdt_pairs = [symbol for symbol in markets if symbol.endswith('/USDT')]
    
    # Sort by base volume (volume is usually found in 'info' for Kucoin)
    sorted_pairs = sorted(
        usdt_pairs,
        key=lambda pair: float(markets[pair].get('info', {}).get('vol', 0)),  # Kucoin'de 'vol' kullanılır
        reverse=True
    )
    return sorted_pairs[:100]

# Fetch market data and analyze
def get_market_data(pair):
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe='5m', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching data for {pair}: {e}")
        return pd.DataFrame()

# Perform technical analysis
def analyze_technical_indicators(df):
    if df.empty:
        return None
    try:
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        return df
    except Exception as e:
        print(f"Error performing technical analysis: {e}")
        return None

# Generate trading signals
def generate_trading_signal(df):
    last_row = df.iloc[-1]
    rsi = last_row['rsi']
    macd = last_row['macd']
    macd_signal = last_row['macd_signal']
    if rsi < 30 and macd > macd_signal:  # RSI low and MACD buy signal
        return "Buy"
    elif rsi > 70 and macd < macd_signal:  # RSI high and MACD sell signal
        return "Sell"
    else:
        return "Neutral"

# Scan the top 100 USDT pairs
def scan_top_usdt_pairs():
    usdt_pairs = fetch_top_100_usdt_pairs()
    results = []
    print("Scanning top 100 USDT pairs...")
    for pair in usdt_pairs:
        df = get_market_data(pair)
        if df.empty:
            continue
        df = analyze_technical_indicators(df)
        if df is None:
            continue
        signal = generate_trading_signal(df)
        if signal in ["Buy", "Sell"]:
            last_price = df['close'].iloc[-1]
            results.append({
                'pair': pair,
                'signal': signal,
                'last_price': last_price
            })
    print("Scan complete.")
    return results

# Send Telegram message
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print("Message sent to Telegram.")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# Send trading signals
async def send_signals():
    results = scan_top_usdt_pairs()
    if not results:
        await send_telegram_message("No Buy/Sell signals found.")
        return
    message = "📊 **Market Signals**\n\n"
    for result in results:
        message += f"{'🟢' if result['signal'] == 'Buy' else '🔴'} Pair: {result['pair']}\nSignal: {result['signal']}\nLast Price: {result['last_price']:.6f} USDT\n\n"
    await send_telegram_message(message)

# Telegram commands
async def start(update, context):
    await update.message.reply_text("Welcome! Use /signals to get the latest market signals.")

async def manual_send_signals(update, context):
    await send_signals()

# Run the bot
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signals", manual_send_signals))
    # Start the bot and send signals
    await application.initialize()
    await application.start()
    try:
        while True:
            await send_signals()
            await asyncio.sleep(300)  # Wait for 5 minutes
    finally:
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())