from datetime import datetime, timedelta
from pymysql import connect
import aiomysql
import pytz

from scripts.config import DB_NAME, DB_USER, DB_HOST, DB_PASSWORD
from scripts.models import User, Action, Ticker


async def create_con(loop):
    con = await aiomysql.connect(host=DB_HOST, user=DB_USER, db=DB_NAME, password=DB_PASSWORD, loop=loop)
    cur = await con.cursor()
    return con, cur


def create_sync_con():
    con = connect(host=DB_HOST, user=DB_USER, db=DB_NAME, password=DB_PASSWORD)
    cur = con.cursor()
    return con, cur


class UsersDbManager:
    @staticmethod
    async def user_exist(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select count(*) from users where tel_id = %s', tel_id)
        r = await cur.fetchone()
        count = r[0]
        return count > 0

    @staticmethod
    async def delete(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute(f'delete from users where tel_id = {tel_id}')
        await con.commit()
        con.close()

    @staticmethod
    async def add_user(tel_id, username, name, language_code, loop):
        con, cur = await create_con(loop)
        utc_now = pytz.utc.localize(datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
        await cur.execute('insert into users (tel_id, username, name, language_code, is_admin, subscribe_date, context) values(%s, %s, %s, %s, %s, %s, %s)', (tel_id, username, name, language_code, 1, date_time_now, "0"))
        await con.commit()
        con.close()

        await ActionsDbManager.add(tel_id, 'subscribe', loop)

    @staticmethod
    async def get_user(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute(f'select * from users where tel_id = {tel_id}')
        user = await cur.fetchone()
        con.close()

        if user is None:
            return None

        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])

    @staticmethod
    async def get_all_users(loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users')
        users = await cur.fetchall()
        con.close()

        result = []
        for user in users:
            result.append(User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7]))
        return result

    @staticmethod
    async def update_context(tel_id, context, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set context = %s where tel_id = %s', (context, tel_id))
        await con.commit()
        con.close()

    @staticmethod
    def sync_get_context(tel_id):
        con, cur = create_sync_con()
        cur.execute(f'select context from users where tel_id = {tel_id}')
        context = cur.fetchone()
        con.close()

        if context is None:
            return None

        return context[0]


class ActionsDbManager:
    @staticmethod
    async def add(tel_id, type, loop, ticker=None, ticker_field=None, new_value=None):
        con, cur = await create_con(loop)
        utc_now = pytz.utc.localize(datetime.utcnow())
        date = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
        await cur.execute('insert into actions (tel_id, type, date, ticker, ticker_field, new_value) values(%s, %s, %s, %s, %s, %s)', (tel_id, type, date, ticker, ticker_field, new_value))
        await con.commit()
        con.close()

    @staticmethod
    async def delete_by_tel_id(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute(f'delete from actions where tel_id = {tel_id}')
        await con.commit()
        con.close()

    @staticmethod
    async def get_last_activity_tel_id(tel_id, loop, actions_count=10):
        con, cur = await create_con(loop)
        await cur.execute('select * from actions where tel_id = %s order by date desc limit %s', (tel_id, actions_count))
        actions = await cur.fetchall()
        con.close()

        result = []
        for action in actions:
            result.append(Action(action[0], action[1], action[2], action[3], action[4], action[5], action[6]))
        return result


class TickerDbManager:
    @staticmethod
    async def add(tel_id, ticker, percent, period, last_price_usd, loop):
        con, cur = await create_con(loop)
        utc_now = pytz.utc.localize(datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
        next_update = date_time_now + timedelta(minutes=period)
        await cur.execute('insert into ticker (tel_id, ticker, percent, period, last_price_usd, next_update) values(%s, %s, %s, %s, %s, %s)', (tel_id, ticker, percent, period, last_price_usd, next_update))
        await con.commit()
        con.close()

        await ActionsDbManager.add(tel_id, 'ticker_add', loop, ticker)

    @staticmethod
    async def get_by_tel_id(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute(f'select * from ticker where tel_id = {tel_id}')
        tickers = await cur.fetchall()
        con.close()

        result = []
        for ticker in tickers:
            result.append(Ticker(ticker[0], ticker[1], ticker[2], ticker[3], ticker[4], ticker[5], ticker[6]))
        return result

    @staticmethod
    async def get_tickers_to_update(loop):
        con, cur = await create_con(loop)

        utc_now = pytz.utc.localize(datetime.utcnow())
        date_time_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))

        await cur.execute('select * from ticker where next_update <= %s', date_time_now)
        tickers = await cur.fetchall()
        con.close()

        result = []
        for ticker in tickers:
            result.append(Ticker(ticker[0], ticker[1], ticker[2], ticker[3], ticker[4], ticker[5], ticker[6]))
        return result

    @staticmethod
    async def get(id, loop):
        con, cur = await create_con(loop)
        await cur.execute(f'select * from ticker where id = {id}')
        ticker = await cur.fetchone()
        con.close()

        if ticker is None:
            return None

        return Ticker(ticker[0], ticker[1], ticker[2], ticker[3], ticker[4], ticker[5], ticker[6])

    @staticmethod
    async def delete(id, loop):
        ticker = await TickerDbManager.get(id, loop)
        con, cur = await create_con(loop)
        await cur.execute(f'delete from ticker where id = {id}')
        await con.commit()
        con.close()

        await ActionsDbManager.add(ticker.tel_id, 'ticker_delete', loop, ticker.ticker)

    @staticmethod
    async def delete_by_tel_id(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute(f'delete from ticker where tel_id = {tel_id}')
        await con.commit()
        con.close()

    @staticmethod
    async def update_percent(id, new_percent, loop):
        ticker = await TickerDbManager.get(id, loop)

        con, cur = await create_con(loop)
        await cur.execute('update ticker set percent = %s where id = %s', (new_percent, id))
        await con.commit()
        con.close()

        await ActionsDbManager.add(ticker.tel_id, 'ticker_edit', loop, ticker.ticker, 'percent', new_percent)

    @staticmethod
    async def update_period(id, new_period, loop):
        ticker = await TickerDbManager.get(id, loop)

        con, cur = await create_con(loop)
        await cur.execute('update ticker set period = %s where id = %s', (new_period, id))
        await con.commit()
        con.close()

        await ActionsDbManager.add(ticker.tel_id, 'ticker_edit', loop, ticker.ticker, 'period', new_period)

    @staticmethod
    async def update_last_price_usd(id, new_last_price_usd, loop):
        con, cur = await create_con(loop)
        await cur.execute('update ticker set last_price_usd = %s where id = %s', (new_last_price_usd, id))
        await con.commit()
        con.close()

    @staticmethod
    async def update_next_update(id, new_next_update, loop):
        con, cur = await create_con(loop)
        await cur.execute('update ticker set next_update = %s where id = %s', (new_next_update, id))
        await con.commit()
        con.close()
