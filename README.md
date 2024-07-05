# Crypto-trading-bot
This bot helps you effortlessly copy trades from Telegram channels and execute them on major cryptocurrency exchanges. Happy trading!

## HOW TO USE?
The bot will automatically start listening to messages from the configured Telegram source channel. When it detects a trade signal, it will process the information and execute the corresponding trade on your configured cryptocurrency exchange.
1) Replace the placeholders with your actual values:
 ```
  api_id = 'YOUR_API_ID'
  api_hash = 'YOUR_API_HASH'
  source_channel = 'YOUR_SOURCE_CHANNEL_ID'
  destination_channel = 'YOUR_DESTINATION_CHANNEL_ID'
  test = 'YOUR_TEST_CHANNEL_ID'
  orig = 'YOUR_ORIGINAL_CHANNEL_ID'

  bybit = HTTP(testnet=False,
               api_key="YOUR_API_KEY",
               api_secret="YOUR_API_SECRET")
```
2) Execute the bot by running the main script
3) PROFIT!
