import hmac
import pprint
import time
from hashlib import sha256

import requests

APIURL = "https://open-api.bingx.com"
APIKEY = "0AmO4AG3tJUhRKEcnM7UTwVSeZ3XQyWnTNQSDhGfKyn6D6yp9FKHLs8wz2iEhVUNswyrawOvcHkE3IWiOaewJQ"
SECRETKEY = "ukvwXsBH4tzk2VCB9mVuuI83MtNOTIdlymfKRQUeKnEwNGdtegJx7HgIgkOg88Blb08LOjhNLFQO9ySqaQbw"


def demo(symbol, side, positionSide, leverage, quantity):
    # def demo():
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    paramsMap = {
        "symbol": symbol,
        "side": side,  # buy-sell
        "positionSide": positionSide,  # long-short
        "type": "MARKET",
        'leverage': leverage,
        'quantity': quantity
    }
    # paramsMap = {
    #     'side': 'BUY',
    #     'positionSide': 'LONG',
    #     'symbol': 'XRP-USDT',
    #     'leverage': 5,
    #     'margin': 2,
    #     'type': 'MARKET',
    #     'workingType': 'MARK_PRICE'
    #
    # }
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)


def get_balance():
    payload = {}
    path = '/openApi/swap/v2/user/balance'
    method = "GET"
    paramsMap_balance = {
        "timestamp": str(int(time.time() * 1000))
    }
    paramsStr_balance = parseParam(paramsMap_balance)
    return send_request(method, path, paramsStr_balance, payload)


def get_price(coin):
    payload = {}
    path = '/openApi/swap/v2/quote/ticker'
    method = "GET"
    paramsMap_balance = {
        "timestamp": str(int(time.time() * 1000)),
        'symbol': coin
    }

    paramsStr_balance = parseParam(paramsMap_balance)
    return send_request(method, path, paramsStr_balance, payload)


def get_min_price():
    payload = {}
    path = '/openApi/swap/v2/quote/contracts'
    method = "GET"
    paramsMap_min_price = {
        "timestamp": str(int(time.time() * 1000))
    }

    paramsStr_min_price = parseParam(paramsMap_min_price)
    return send_request(method, path, paramsStr_min_price, payload)


def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    # print("sign=" + signature)
    return signature


def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    # print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload).json()

    return response


def parseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    if paramsStr != "":
        return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
    else:
        return paramsStr + "timestamp=" + str(int(time.time() * 1000))

# pprint.pprint(get_price('1000PEPE-USDT'))
# pprint.pprint(get_price('SAND-USDT'))
#
# import pprint
# pprint.pprint(get_price('BTC-USDT'))

# for i in get_min_price()['data']:
#     if i['maxLongLeverage'] > 10:
#         pprint.pprint(i)

# for i in get_min_price()['data']:
#     if i['symbol'] == 'SAND-USDT':
#         pprint.pprint(i)
