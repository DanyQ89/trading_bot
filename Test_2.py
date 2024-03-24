import hmac
import time
from hashlib import sha256

import requests

APIURL = "https://open-api.bingx.com"
APIKEY = "0AmO4AG3tJUhRKEcnM7UTwVSeZ3XQyWnTNQSDhGfKyn6D6yp9FKHLs8wz2iEhVUNswyrawOvcHkE3IWiOaewJQ"
SECRETKEY = "ukvwXsBH4tzk2VCB9mVuuI83MtNOTIdlymfKRQUeKnEwNGdtegJx7HgIgkOg88Blb08LOjhNLFQO9ySqaQbw"


# def demo(symbol, side, positionSide, value, leverage, margin):
def demo():
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    # paramsMap = {
    #     "symbol": symbol,
    #     "side": side, #buy-sell
    #     "positionSide": positionSide, #long-short
    #     "type": "MARKET",
    #     "quantity": value,
    #     'leverage': leverage,
    #     'margin': margin
    # }
    paramsMap = {
        'side': 'BUY',
        'positionSide': 'LONG',
        'symbol': 'XRP-USDT',
        'leverage': 5,
        'margin': 2,
        'type': 'MARKET'

    }
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)


def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    print("sign=" + signature)
    return signature


def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.text


def parseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    if paramsStr != "":
        return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
    else:
        return paramsStr + "timestamp=" + str(int(time.time() * 1000))


# if __name__ == '__main__':
#     print("demo:", demo())

try:
    a = demo()
    print(a)
    print('sucess')
except Exception as err:
    print(err)