import json
import aiohttp

from scripts.config import COINMARKETCAP_API_KEY

API_URL = 'https://pro-api.coinmarketcap.com/'

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
}


async def get_price(symbol):
    endpoint = API_URL + 'v1/tools/price-conversion'

    params = {
        'amount': '1',
        'symbol': symbol,
        'convert': 'USD'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(endpoint, params=params) as resp:
            if resp.status == 200:
                body = json.loads(await resp.text())
                price = round(body['data']['quote']['USD']['price'], 4)
                return price
            else:
                return None
