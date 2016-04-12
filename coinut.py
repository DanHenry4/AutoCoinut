import hmac
import hashlib
import json
import uuid

import httplib2

COINUT_URL = 'https://coinut.com/api/'

class Coinut():
    def __init__(self, user = None, api_key = None):
        self.user = user
        self.api_key = api_key
        self.http = httplib2.Http()

    def request(self, api, content = {}):
        url = COINUT_URL + api
        headers = {}
        content["nonce"] = uuid.uuid4().get_hex()
        content = json.dumps(content)

        if self.api_key is not None and self.user is not None:
            sig = hmac.new(self.api_key, msg=content,
                           digestmod=hashlib.sha256).hexdigest()
            headers = {'X-USER': self.user, "X-SIGNATURE": sig}

        response, content = self.http.request(url, 'POST',
                                              headers=headers, body=content)
        return json.loads(content)


    def tick(self, asset):
        return self.request("tick/" + asset)


    def balance(self):
        return self.request("balance")


    def assets(self, deriv_type):
        return self.request("assets", {'deriv_type' : deriv_type})


    def expiry_time(self, deriv_type, asset):
        return self.request("expiry_time",
                              {'deriv_type' : deriv_type,
                               'asset': asset})


    def strike_prices(self, deriv_type, asset, expiry_time):
        m = {
            'deriv_type' : deriv_type,
            'asset': asset,
            'expiry_time': expiry_time
        }

        return self.request("strike_prices", m)


    def orderbook(self, deriv_type, asset, expiry_time, strike, put_call):
        m = {
            'deriv_type' : deriv_type,
            'asset': asset,
            'expiry_time': expiry_time,
            'strike': strike,
            'put_call': put_call
         }

        return self.request('orderbook', m)


    def new_orders(self, orders):
        return self.request("new_orders", {'orders': orders})

    def orders(self):
        return self.request("orders")

    def cancel_orders(self, order_ids):
        return self.request("cancel_orders", {'order_ids': order_ids})

    def positions(self):
        return self.request("positions")

    def history_positions(self, start_timestamp, end_timestamp):
        m = {'start_timestamp': start_timestamp,
             'end_timestamp': end_timestamp}
        return self.request("history_positions", m)
