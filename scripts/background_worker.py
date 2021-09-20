from datetime import datetime, timedelta
from aiogram import Bot
import asyncio
import pytz

from scripts.db_manager import UsersDbManager, ActionsDbManager, TickerDbManager
from scripts.coinmarketcap_api import get_price
from scripts import messages as msg
from scripts.config import TOKEN

bot = Bot(TOKEN)


async def worker(loop):
    while True:
        tickers = await TickerDbManager.get_tickers_to_update(loop)

        for ticker in tickers:
            old_price = ticker.last_price_usd
            new_price = await get_price(ticker.ticker)

            change_percentage = ((new_price - old_price) / old_price) * 100
            change_percentage = round(change_percentage, 2)

            if abs(change_percentage) >= ticker.percent:

                if change_percentage > 0:
                    message = msg.ticker_notification_positive.format(ticker.ticker, abs(change_percentage), new_price)
                else:
                    message = msg.ticker_notification_negative.format(ticker.ticker, abs(change_percentage), new_price)

                try:
                    await bot.send_message(ticker.tel_id, message, parse_mode='html')
                except Exception:
                    pass

                await TickerDbManager.update_last_price_usd(ticker.id, new_price, loop)

            utc_now = pytz.utc.localize(datetime.utcnow())
            date_time_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
            next_update = date_time_now + timedelta(minutes=ticker.period)

            await TickerDbManager.update_next_update(ticker.id, next_update, loop)

        await asyncio.sleep(5)


async def unsubscribe_checker(loop):
    while True:
        users = await UsersDbManager.get_all_users(loop)
        for user in users:
            try:
                await bot.send_chat_action(user.tel_id, 'typing')
            except Exception:
                await UsersDbManager.delete(user.tel_id, loop)
                await ActionsDbManager.delete_by_tel_id(user.tel_id, loop)
                await TickerDbManager.delete_by_tel_id(user.tel_id, loop)

        await asyncio.sleep(5)
