class User:
    def __init__(self, id, tel_id, username, name, language_code, is_admin, subscribe_date, context):
        self.id = id
        self.tel_id = tel_id
        self.username = username
        self.name = name
        self.language_code = language_code
        self.is_admin = is_admin
        self.subscribe_date = subscribe_date
        self.context = context


'''
types:
    subscribe
    ticker_add
    ticker_delete
    ticker_edit

ticker_field:
    percent
    period
'''


class Action:
    def __init__(self, id, tel_id, type, date, ticker, ticker_field, new_value):
        self.id = id
        self.tel_id = tel_id
        self.type = type
        self.date = date
        self.ticker = ticker
        self.ticker_field = ticker_field
        self.new_value = new_value


class Ticker:
    def __init__(self, id, tel_id, ticker, percent, period, last_price_usd, next_update):
        self.id = id
        self.tel_id = tel_id
        self.ticker = ticker
        self.percent = percent
        self.period = period
        self.last_price_usd = last_price_usd
        self.next_update = next_update

