from aiogram import Bot, Dispatcher, executor
from datetime import datetime, timedelta
import asyncio
import logging
import pytz

from scripts.background_worker import worker, unsubscribe_checker
from scripts.db_manager import UsersDbManager, TickerDbManager
from scripts.coinmarketcap_api import get_price
from scripts.config import TOKEN, DEBUG
import scripts.messages as msg
import scripts.markup as mk


bot = Bot(TOKEN)
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    asyncio.run_coroutine_threadsafe(worker(loop), loop)
    asyncio.run_coroutine_threadsafe(unsubscribe_checker(loop), loop)


'''Для пользователей'''


@dp.message_handler(lambda message: message.text == '🏠 В раздел для пользователей')
@dp.message_handler(commands=['start'])
async def start(message):
    tel_id = message.chat.id
    username = message.from_user.username
    name = message.from_user.first_name
    language_code = message.from_user.language_code

    await UsersDbManager.update_context(tel_id, '0', loop)
    await bot.send_chat_action(tel_id, 'typing')

    if not await UsersDbManager.user_exist(tel_id, loop):
        await UsersDbManager.add_user(tel_id, username, name, language_code, loop)
        await bot.send_message(tel_id, msg.greeting, disable_notification=True, parse_mode='HTML', reply_markup=mk.choose_ticker())
        await bot.send_message(tel_id, '<b>Главное меню</b>', reply_markup=mk.main_menu,  disable_notification=True, parse_mode='HTML')
        return
    else:
        await bot.send_message(tel_id, '<b>Главное меню</b>', reply_markup=mk.main_menu, disable_notification=True, parse_mode='HTML')


@dp.callback_query_handler(lambda call: call.data.startswith('back-'))
async def back(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    section = call.data.split('-')[-1]

    if section == 'add_ticker_choose_ticker':
        try:
            await bot.edit_message_text(msg.choose_ticker, tel_id, message_id, parse_mode='html', reply_markup=mk.choose_ticker())
            await UsersDbManager.update_context(tel_id, '0', loop)
        except Exception:
            pass
    elif section == 'add_ticker_choose_percent':
        try:
            ticker = call.data.split('-')[-2]
            await bot.edit_message_text(msg.ticker_chosen.format(ticker), tel_id, message_id, parse_mode='html', reply_markup=mk.back('back-add_ticker_choose_ticker'))
            await UsersDbManager.update_context(tel_id, f'add_ticker-{ticker}-choose_percent', loop)
        except Exception:
            pass
    elif section == 'my_tickers':
        try:
            keyboard, text = await mk.get_my_ticker_content(tel_id, loop)
            await bot.edit_message_text(text, tel_id, message_id, parse_mode='html', reply_markup=keyboard)
            await UsersDbManager.update_context(tel_id, '0', loop)
        except Exception:
            pass
    elif section == 'user_info':
        user_id = int(call.data.split('-')[-2])
        keyboard, text = await mk.get_user_base_info(user_id, loop)
        try:
            await bot.edit_message_text(text, tel_id, message_id, parse_mode='html', reply_markup=keyboard)
        except Exception:
            pass


@dp.callback_query_handler(lambda call: call.data == 'add_ticker')
async def add_ticker(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    tickers = await TickerDbManager.get_by_tel_id(tel_id, loop)
    if len(tickers) >= 10:
        await bot.send_message(tel_id, msg.cant_add_more_tickers, disable_notification=True, parse_mode='HTML')
        return

    try:
        await bot.edit_message_text(msg.choose_ticker, tel_id, message_id, parse_mode='html', reply_markup=mk.choose_ticker_back('back-my_tickers'))
        await UsersDbManager.update_context(tel_id, '0', loop)
    except Exception:
        pass


@dp.callback_query_handler(lambda call: call.data.startswith('add_ticker-choose_ticker-'))
async def add_ticker(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    ticker = call.data.split('-')[-1]

    if ticker != 'OPTIONAL':
        try:
            await bot.edit_message_text(msg.ticker_chosen.format(ticker), tel_id, message_id, parse_mode='html', reply_markup=mk.back('back-add_ticker_choose_ticker'))
            await UsersDbManager.update_context(tel_id, f'add_ticker-{ticker}-choose_percent', loop)
        except Exception:
            pass
    else:
        try:
            await bot.edit_message_text(msg.choose_ticker_manual, tel_id, message_id, parse_mode='html', reply_markup=mk.back('back-add_ticker_choose_ticker'))
            await UsersDbManager.update_context(tel_id, 'add_ticker-choose_ticker', loop)
        except Exception:
            pass


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id).startswith('add_ticker-'), content_types=['text'])
async def add_ticker(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    operation = user.context.split('-')[-1]

    if operation == 'choose_ticker':
        ticker = message.text.upper()
        price = get_price(ticker)

        if price is None:
            await bot.send_message(tel_id, msg.ticker_not_exist.format(ticker), disable_notification=True, parse_mode='HTML')
            return

        await bot.send_message(tel_id, msg.ticker_chosen.format(ticker), disable_notification=True, parse_mode='HTML', reply_markup=mk.back('back-add_ticker_choose_ticker'))
        await UsersDbManager.update_context(tel_id, f'add_ticker-{ticker}-choose_percent', loop)
    elif operation == 'choose_percent':
        ticker = user.context.split('-')[-2]
        percent = message.text.replace(',', '.').replace('%', '')

        try:
            percent = float(percent)
        except Exception:
            await bot.send_message(tel_id, msg.percent_invalid, disable_notification=True)
            return

        percent = round(percent, 2)

        if percent == 0:
            await bot.send_message(tel_id, msg.percent_too_little, disable_notification=True)
            return

        await bot.send_message(tel_id, msg.choose_period.format(percent), disable_notification=True, parse_mode='HTML', reply_markup=mk.choose_period(f'back-{ticker}-add_ticker_choose_percent'))
        await UsersDbManager.update_context(tel_id, f'add_ticker-{ticker}-{percent}-choose_period', loop)
    elif operation == 'choose_period':
        ticker = user.context.split('-')[-3]
        percent = float(user.context.split('-')[-2])

        try:
            period = int(message.text)
        except Exception:
            await bot.send_message(tel_id, msg.period_invalid, disable_notification=True)
            return

        await bot.send_message(tel_id, msg.ticker_added.format(ticker, period, percent), disable_notification=True, parse_mode='HTML')
        await UsersDbManager.update_context(tel_id, '0', loop)
        last_price_usd = await get_price(ticker)
        await TickerDbManager.add(tel_id, ticker, percent, period, last_price_usd, loop)


@dp.callback_query_handler(lambda call: call.data.startswith('add_ticker-choose_period-') and UsersDbManager.sync_get_context(call.message.chat.id).endswith('-choose_period'))
async def add_ticker(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    user = await UsersDbManager.get_user(tel_id, loop)

    ticker = user.context.split('-')[-3]
    percent = user.context.split('-')[-2]
    period = call.data.split('-')[-1]

    if period != 'OPTIONAL':
        try:
            period = int(period)
            await bot.edit_message_text(msg.ticker_added.format(ticker, period, percent), tel_id, message_id, parse_mode='html')
            await UsersDbManager.update_context(tel_id, '0', loop)
            last_price_usd = await get_price(ticker)
            await TickerDbManager.add(tel_id, ticker, percent, period, last_price_usd, loop)
        except Exception:
            pass
    else:
        try:
            await bot.edit_message_text(msg.choose_period_manual, tel_id, message_id, parse_mode='html', reply_markup=mk.back(f'back-{ticker}-add_ticker_choose_percent'))
            await UsersDbManager.update_context(tel_id, f'add_ticker-{ticker}-{percent}-choose_period', loop)
        except Exception:
            pass


@dp.message_handler(lambda message: message.text == 'Мои тикеры')
async def my_tickers(message):
    tel_id = message.chat.id
    await UsersDbManager.update_context(tel_id, '0', loop)

    keyboard, text = await mk.get_my_ticker_content(tel_id, loop)
    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('edit_ticker-'))
async def edit_ticker(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    ticker_id = int(call.data.split('-')[-1])

    keyboard, text = await mk.get_edit_ticker_content(ticker_id, loop)

    await UsersDbManager.update_context(tel_id, '0', loop)

    if keyboard is None:
        await my_tickers(call.message)
        await bot.delete_message(tel_id, message_id)
        return

    try:
        await bot.edit_message_text(text, tel_id, message_id, parse_mode='html', reply_markup=keyboard)
    except Exception:
        pass


@dp.callback_query_handler(lambda call: call.data.startswith('edit_ticker_field-'))
async def edit_ticker_field(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    ticker_id = int(call.data.split('-')[-1])

    field = call.data.split('-')[-2]

    ticker = await TickerDbManager.get(ticker_id, loop)
    if ticker is None:
        await my_tickers(call.message)
        await bot.delete_message(tel_id, message_id)
        return

    if field == 'delete':
        await TickerDbManager.delete(ticker_id, loop)
        await bot.delete_message(tel_id, message_id)
        await my_tickers(call.message)
    elif field == 'percent':
        try:
            await bot.edit_message_text(msg.send_new_percent, tel_id, message_id, parse_mode='html', reply_markup=mk.back(f'edit_ticker-{ticker_id}'))
            await UsersDbManager.update_context(tel_id, f'edit_ticker_field-percent-{ticker_id}', loop)
        except Exception:
            pass
    elif field == 'period':
        try:
            await bot.edit_message_text(msg.send_new_period, tel_id, message_id, parse_mode='html', reply_markup=mk.edit_period(ticker_id, f'edit_ticker-{ticker_id}'))
            await UsersDbManager.update_context(tel_id, f'edit_ticker_field-period-{ticker_id}', loop)
        except Exception:
            pass
    elif field == 'choose_period':
        option = call.data.split('-')[-3]

        if option != 'OPTIONAL':
            period = int(option)
            await TickerDbManager.update_period(ticker_id, period, loop)

            price = await get_price(ticker.ticker)
            await TickerDbManager.update_last_price_usd(ticker_id, price, loop)

            utc_now = pytz.utc.localize(datetime.utcnow())
            date_time_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
            next_update = date_time_now + timedelta(minutes=period)
            await TickerDbManager.update_next_update(ticker_id, next_update, loop)

            try:
                await bot.edit_message_text(msg.period_updated.format(ticker.ticker), tel_id, message_id, parse_mode='html')
            except Exception:
                pass

            keyboard, text = await mk.get_edit_ticker_content(ticker_id, loop)
            await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML', reply_markup=keyboard)

            await UsersDbManager.update_context(tel_id, '0', loop)
        else:
            try:
                await bot.edit_message_text(msg.choose_new_period_manual, tel_id, message_id, parse_mode='html', reply_markup=mk.back(f'edit_ticker-{ticker_id}'))
            except Exception:
                pass


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id).startswith('edit_ticker_field-'), content_types=['text'])
async def edit_ticker_field(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    ticker_id = int(user.context.split('-')[-1])
    ticker = await TickerDbManager.get(ticker_id, loop)
    field = user.context.split('-')[-2]

    if field == 'percent':
        try:
            percent = message.text.replace(',', '.').replace('%', '')
            percent = float(percent)
        except Exception:
            await bot.send_message(tel_id, msg.percent_invalid, disable_notification=True)
            return

        percent = round(percent, 2)

        if percent == 0:
            await bot.send_message(tel_id, msg.percent_too_little, disable_notification=True)
            return

        await TickerDbManager.update_percent(ticker_id, percent, loop)
        await bot.send_message(tel_id, msg.percent_updated.format(ticker.ticker), disable_notification=True, parse_mode='HTML')

        keyboard, text = await mk.get_edit_ticker_content(ticker_id, loop)
        await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML', reply_markup=keyboard)

        await UsersDbManager.update_context(tel_id, '0', loop)
    elif field == 'period':
        try:
            period = int(message.text)
        except Exception:
            await bot.send_message(tel_id, msg.period_invalid, disable_notification=True)
            return

        await bot.send_message(tel_id, msg.period_updated.format(ticker.ticker), disable_notification=True, parse_mode='HTML')
        await TickerDbManager.update_period(ticker_id, period, loop)

        price = await get_price(ticker.ticker)
        await TickerDbManager.update_last_price_usd(ticker_id, price, loop)

        utc_now = pytz.utc.localize(datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
        next_update = date_time_now + timedelta(minutes=period)
        await TickerDbManager.update_next_update(ticker_id, next_update, loop)

        await UsersDbManager.update_context(tel_id, '0', loop)

        keyboard, text = await mk.get_edit_ticker_content(ticker_id, loop)
        await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML', reply_markup=keyboard)


'''Для администраторов/менеджеров'''


@dp.message_handler(lambda message: message.text == '❌ Отмена' and UsersDbManager.sync_get_context(message.chat.id) == 'wait_user_info')
async def cancel(message):
    tel_id = message.chat.id
    await UsersDbManager.update_context(tel_id, '0', loop)
    await bot.send_message(tel_id, 'Операция отменена', reply_markup=mk.admin_menu, disable_notification=True)


@dp.message_handler(commands=['admin'])
async def admin(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if not user.is_admin:
        await bot.send_message(tel_id, msg.permission_denied, disable_notification=True, parse_mode='html')
        return

    await bot.send_message(tel_id, 'Панель администратора', reply_markup=mk.admin_menu, disable_notification=True)


@dp.message_handler(lambda message: message.text == '👤 Посмотреть информацию по пользователю')
async def user_info(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if not user.is_admin:
        await bot.send_message(tel_id, msg.permission_denied, disable_notification=True, parse_mode='html')
        return

    await bot.send_message(tel_id, msg.send_me_user, reply_markup=mk.cancel, disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_user_info', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_user_info', content_types=['text'])
async def wait_user_info(message):
    tel_id = message.chat.id

    if message.forward_from is not None:
        user_id = message.forward_from.id
    else:
        try:
            user_id = int(message.text)
        except Exception:
            await bot.send_message(tel_id, msg.user_id_invalid, reply_markup=mk.cancel, disable_notification=True)
            return

    user = await UsersDbManager.get_user(user_id, loop)
    if user is None:
        await bot.send_message(tel_id, msg.user_not_found, reply_markup=mk.cancel, disable_notification=True, parse_mode='html')
        return

    keyboard, text = await mk.get_user_base_info(tel_id, loop)

    await bot.send_message(tel_id, 'Пользователь найден', reply_markup=mk.admin_menu, disable_notification=True, parse_mode='html')
    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True, parse_mode='html')
    await UsersDbManager.update_context(tel_id, '0', loop)


@dp.callback_query_handler(lambda call: call.data.startswith('user_info-'))
async def user_info(call):
    tel_id = call.message.chat.id
    message_id = call.message.message_id

    user_id = int(call.data.split('-')[-1])

    field = call.data.split('-')[-2]

    if field == 'subscriptions':
        keyboard, text = await mk.get_user_subscriptions_info(user_id, loop)

        try:
            await bot.edit_message_text(text, tel_id, message_id, parse_mode='html', reply_markup=keyboard)
        except Exception:
            pass
    elif field == 'last_activity':
        keyboard, text = await mk.get_user_last_activity_info(user_id, loop)

        try:
            await bot.edit_message_text(text, tel_id, message_id, parse_mode='html', reply_markup=keyboard)
        except Exception:
            pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)