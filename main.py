from pyrogram import Client, filters
import re
from pybit.unified_trading import HTTP

# Removed sensitive information
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
source_channel = 'YOUR_SOURCE_CHANNEL_ID'
destination_channel = 'YOUR_DESTINATION_CHANNEL_ID'
test = 'YOUR_TEST_CHANNEL_ID'
orig = 'YOUR_ORIGINAL_CHANNEL_ID'

app = Client("my_account", api_id=api_id, api_hash=api_hash)

# Initialize Bybit API client
bybit = HTTP(testnet=False,
             api_key="YOUR_API_KEY",
             api_secret="YOUR_API_SECRET")


def extract_info(message_text):
    """
    Extracts necessary information from different types of messages.
    """
    # Pattern for the first and second message types (simple)
    simple_pattern = re.search(r"(\w+)\s+(LONG|SHORT)\s*\n\nПлечо\s+(\d+)(?:\s+маржа\s+(\d+))?", message_text,
                               re.IGNORECASE)

    # Pattern for the detailed message type
    detailed_pattern = re.search(
        r"🗯\s*(\w+)\s+Берем\s+(LONG|SHORT).*?Монета:\s*(\w+/USDT).*?Моя точка входа:\s*(\d+\.?\d*).*?Стоп:\s*(\d+\.?\d*).*?(\d+\.?\d*),",
        message_text, re.DOTALL)

    if simple_pattern:
        coin = simple_pattern.group(1) + "USDT"  # Assuming all coins are traded against USDT
        deal_direction = simple_pattern.group(2)
        leverage = simple_pattern.group(3)
        margin = simple_pattern.group(4) if simple_pattern.group(4) else None
        return coin, deal_direction, None, None, None, True

    elif detailed_pattern:
        coin = detailed_pattern.group(3)
        deal_direction = detailed_pattern.group(2)
        entry_point = detailed_pattern.group(4)
        stop_loss = detailed_pattern.group(5)
        first_tp = detailed_pattern.group(6)
        return coin, deal_direction, entry_point, stop_loss, first_tp, False

    return None, None, None, None, None, False


@app.on_message(filters.channel & filters.chat(source_channel))
def from_channel(client, message):
    message_text = message.text or message.caption

    if message_text is None:
        print("Сообщение не содержит текста.")
        return  # Пропускаем обработку, если нет текста и подписи
    else:
        client.send_message(destination_channel, message_text)

    coin, deal_direction, entry_price, stop_loss1, take_profit1, isQuick = extract_info(message_text)

    client.send_message(destination_channel, f"Сообщение получено")
    if coin and deal_direction:
        try:
            symbol = f"{coin}"
            leverage = 20  # Ensure this formats the symbol correctly.

            side = "Buy" if deal_direction == "LONG" else "Sell"
            qty = 1
            try:
                bybit.set_leverage(
                    category="linear",
                    symbol=symbol,
                    buyLeverage=leverage,
                    sellLeverage=leverage,
                )

                bybit.switch_position_mode(
                    category="linear",
                    symbol=symbol,
                    mode=0,
                )
            except:
                ...

            # Place a market order
            try:
                response = bybit.place_order(
                    category="linear",
                    symbol=symbol,
                    side=side,
                    orderType="Market",
                    qty=str(qty),
                )

                price = bybit.get_positions(
                    category="linear",
                    symbol=symbol,
                )

                entry_price = price['result']['list'][0]['avgPrice']
                if deal_direction == "Buy":
                    take_profit1 = str(float(entry_price) * 1.3)
                    stop_loss1 = str(float(entry_price) * 0.7)
                else:
                    take_profit1 = str(float(entry_price) * 0.7)
                    take_profit1 = take_profit1[0:8]
                    stop_loss1 = str(float(entry_price) * 1.3)
                    stop_loss1 = stop_loss1[0:8]
                print(entry_price)
                print(take_profit1)
                print(stop_loss1)

                bybit.set_trading_stop(
                    category="linear",
                    symbol=symbol,
                    takeProfit=take_profit1,
                    stopLoss=stop_loss1,
                    tpslMode="Full",
                    positionIdx=0,
                )
                client.send_message(destination_channel,
                                    "Открыл сделку на " + coin + str(entry_price) + " тп и сл " + str(
                                        take_profit1) + ' ' + str(stop_loss1))
            except AttributeError:
                print("The method for placing an order is not available in your version of pybit.")
            except Exception as e:
                print("An error occurred:", str(e))

        except Exception as e:
            client.send_message(destination_channel, f"An error occurred: {str(e)}")


app.run()
