from aiogram.types import reply_keyboard, inline_keyboard

import scripts.messages as msg
from scripts.db_manager import TickerDbManager, UsersDbManager, ActionsDbManager

admin_menu = reply_keyboard.ReplyKeyboardMarkup([['👤 Посмотреть информацию по пользователю'],
                                                 ['🏠 В раздел для пользователей']], resize_keyboard=True)

main_menu = reply_keyboard.ReplyKeyboardMarkup([['Мои тикеры']], resize_keyboard=True)

cancel = reply_keyboard.ReplyKeyboardMarkup([['❌ Отмена']], resize_keyboard=True)


def choose_ticker():
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('BTC', callback_data=f'add_ticker-choose_ticker-BTC'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('ETH', callback_data=f'add_ticker-choose_ticker-ETH'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('ADA', callback_data=f'add_ticker-choose_ticker-ADA'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('BNB', callback_data=f'add_ticker-choose_ticker-BNB'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('USDT', callback_data=f'add_ticker-choose_ticker-USDT'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('XPR', callback_data=f'add_ticker-choose_ticker-XPR'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('SOL', callback_data=f'add_ticker-choose_ticker-SOL'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('DOT', callback_data=f'add_ticker-choose_ticker-DOT'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('DOGE', callback_data=f'add_ticker-choose_ticker-DOGE'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('USDC', callback_data=f'add_ticker-choose_ticker-USDC'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('Ввести вручную', callback_data=f'add_ticker-choose_ticker-OPTIONAL'))
    return keyboard


def choose_ticker_back(back_call_data):
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('BTC', callback_data=f'add_ticker-choose_ticker-BTC'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('ETH', callback_data=f'add_ticker-choose_ticker-ETH'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('ADA', callback_data=f'add_ticker-choose_ticker-ADA'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('BNB', callback_data=f'add_ticker-choose_ticker-BNB'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('USDT', callback_data=f'add_ticker-choose_ticker-USDT'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('XPR', callback_data=f'add_ticker-choose_ticker-XPR'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('SOL', callback_data=f'add_ticker-choose_ticker-SOL'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('DOT', callback_data=f'add_ticker-choose_ticker-DOT'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('DOGE', callback_data=f'add_ticker-choose_ticker-DOGE'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('USDC', callback_data=f'add_ticker-choose_ticker-USDC'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('Ввести вручную', callback_data=f'add_ticker-choose_ticker-OPTIONAL'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data=back_call_data))
    return keyboard


def choose_period(back_call_data):
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('5 минут', callback_data=f'add_ticker-choose_period-5'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('10 минут', callback_data=f'add_ticker-choose_period-10'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('1 час', callback_data=f'add_ticker-choose_period-60'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('1 день', callback_data=f'add_ticker-choose_period-1440'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('Ввести вручную', callback_data=f'add_ticker-choose_period-OPTIONAL'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data=back_call_data))
    return keyboard


def edit_period(ticker_id, back_call_data):
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('5 минут', callback_data=f'edit_ticker_field-5-choose_period-{ticker_id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('10 минут', callback_data=f'edit_ticker_field-10-choose_period-{ticker_id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('1 час', callback_data=f'edit_ticker_field-60-choose_period-{ticker_id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('1 день', callback_data=f'edit_ticker_field-1440-choose_period-{ticker_id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('Ввести вручную', callback_data=f'edit_ticker_field-OPTIONAL-choose_period-{ticker_id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data=back_call_data))
    return keyboard


def back(call_data):
    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data=call_data))
    return keyboard


async def get_my_ticker_content(tel_id, loop):
    tickers = await TickerDbManager.get_by_tel_id(tel_id, loop)

    keyboard = inline_keyboard.InlineKeyboardMarkup()

    if len(tickers) > 0:
        ticker_header = inline_keyboard.InlineKeyboardButton('Тикер', callback_data='0')
        percent_header = inline_keyboard.InlineKeyboardButton('Процент', callback_data='0')
        period_header = inline_keyboard.InlineKeyboardButton('Период', callback_data='0')

        keyboard.add(ticker_header, percent_header, period_header)

    for ticker in tickers:
        ticker_item = inline_keyboard.InlineKeyboardButton(ticker.ticker, callback_data=f'edit_ticker-{ticker.id}')
        percent_item = inline_keyboard.InlineKeyboardButton(f'{ticker.percent}%', callback_data=f'edit_ticker-{ticker.id}')
        period_item = inline_keyboard.InlineKeyboardButton(f'{ticker.period} мин', callback_data=f'edit_ticker-{ticker.id}')

        keyboard.add(ticker_item, percent_item, period_item)

    if len(tickers) < 10:
        keyboard.add(inline_keyboard.InlineKeyboardButton('➕ Добавить', callback_data=f'add_ticker'))

    if len(tickers) > 0:
        text = msg.your_tickers
    else:
        text = msg.no_tickers

    return keyboard, text


async def get_edit_ticker_content(id, loop):
    ticker = await TickerDbManager.get(id, loop)

    if ticker is None:
        return None, None

    text = f'''<b>Тикер:</b> {ticker.ticker}

<b>Процент:</b> {ticker.percent}%

<b>Период:</b> {ticker.period} мин

<b>Следующее обновление:</b> {ticker.next_update}

<b>Последняя стоимость:</b> {ticker.last_price_usd} USD'''

    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('Изменить процент', callback_data=f'edit_ticker_field-percent-{ticker.id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('Изменить период', callback_data=f'edit_ticker_field-period-{ticker.id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('🗑 Удалить', callback_data=f'edit_ticker_field-delete-{ticker.id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data='back-my_tickers'))

    return keyboard, text


async def get_user_base_info(tel_id, loop):
    user = await UsersDbManager.get_user(tel_id, loop)

    username_text = user.username
    if username_text is None:
        username_text = '---'

    text = f'''👤 Информация по пользователю с id <b>{user.tel_id}</b>

<b>Ник:</b> {username_text}

<b>Имя в Telegram:</b> {user.name}

<b>Язык в настройках Telegram:</b> {user.language_code}

<b>Дата и время подписки на бот:</b> {user.subscribe_date}'''

    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('Активные подписки', callback_data=f'user_info-subscriptions-{user.tel_id}'))
    keyboard.add(inline_keyboard.InlineKeyboardButton('Последние действия', callback_data=f'user_info-last_activity-{user.tel_id}'))

    return keyboard, text


async def get_user_subscriptions_info(tel_id, loop):
    user = await UsersDbManager.get_user(tel_id, loop)

    text = f'''👤 Активные подписки пользователя с id <b>{user.tel_id}</b>'''

    tickers = await TickerDbManager.get_by_tel_id(tel_id, loop)

    keyboard = inline_keyboard.InlineKeyboardMarkup()

    if len(tickers) > 0:
        ticker_header = inline_keyboard.InlineKeyboardButton('Тикер', callback_data='0')
        percent_header = inline_keyboard.InlineKeyboardButton('Процент', callback_data='0')
        period_header = inline_keyboard.InlineKeyboardButton('Период', callback_data='0')

        keyboard.add(ticker_header, percent_header, period_header)

    for ticker in tickers:
        ticker_item = inline_keyboard.InlineKeyboardButton(ticker.ticker, callback_data='0')
        percent_item = inline_keyboard.InlineKeyboardButton(f'{ticker.percent}%', callback_data='0')
        period_item = inline_keyboard.InlineKeyboardButton(f'{ticker.period} мин', callback_data='0')

        keyboard.add(ticker_item, percent_item, period_item)

    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data=f'back-{tel_id}-user_info'))

    return keyboard, text


async def get_user_last_activity_info(tel_id, loop):
    user = await UsersDbManager.get_user(tel_id, loop)

    actions = await ActionsDbManager.get_last_activity_tel_id(tel_id, loop)

    content = ''''''
    for action in actions:
        if action.type == 'subscribe':
            content += f'''

Подписался ({action.date})'''
        elif action.type == 'ticker_add':
            content += f'''

Добавил тикер {action.ticker} ({action.date})'''
        elif action.type == 'ticker_delete':
            content += f'''

Удалил тикер {action.ticker} ({action.date})'''
        elif action.type == 'ticker_edit':
            if action.ticker_field == 'percent':
                ticker_field_text = 'процента'
            elif action.ticker_field == 'period':
                ticker_field_text = 'периода'

            content += f'''

Изменил поле {ticker_field_text} тикера {action.ticker} на {action.new_value} ({action.date})'''

    text = f'''👤 Последние действия пользователя с id <b>{user.tel_id}</b>
{content}'''

    keyboard = inline_keyboard.InlineKeyboardMarkup()
    keyboard.add(inline_keyboard.InlineKeyboardButton('« Назад', callback_data=f'back-{tel_id}-user_info'))

    return keyboard, text
