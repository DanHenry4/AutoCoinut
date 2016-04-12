from manager import Manager
from stats import Stats
from datetime import datetime, time
import math
import random
import string
import sys
import time

class AutoTrader(Manager):
    def __init__(self, real_time=False):
        Manager.__init__(self)
        self.real_time = real_time
        self.balance = 1.0
        if self.real_time:
            self.balance = self.GetBTCBalance()
        self.open_orders = []

    def GetBTCBalance(self):
        return float(self.coinut.balance()["free_margin"])

    def GetOptionPrices(self):
        nearest_expiry = self.GetNearestExpiry()
        upper_bound = str(self.GetUpperBound(self.GetCurrentPrice()))
        open_bids = self.coinut.orderbook(
            self.d_type, self.asset, nearest_expiry, upper_bound, self.put_call
        )["bid"]
        return (upper_bound, open_bids)

    # TODO Create Order class instead of using methods inside AutoTrader.
    def OpenOrder(self, expiry, strike, amount, price, buy_sell="SELL"):
        data = [{
            "put_call": self.put_call,
            "expiry_time": int(expiry),
            "asset": self.asset,
            "strike": str(strike),
            "amount": int(amount),
            "price": str(price),
            "open_close": "OPEN",
            "type": "LIMIT",
            "deriv_type": self.d_type,
            "side": buy_sell
        }]
        if self.real_time:
            return self.coinut.new_orders(data)
        else:
            self.balance += float(price) * int(amount)
            rand_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in xrange(36))
            return [{
                "status": "ORDER_OPEN",
                "put_call": self.put_call,
                "expiry_time": int(expiry),
                "timestamp": time.time(),
                "price": str(price),
                "open_close": "OPEN",
                "deriv_type": self.d_type,
                "side": buy_sell,
                "amount": int(amount),
                "asset": self.asset,
                "strike": str(strike),
                "type": "LIMIT",
                "id": rand_id
            }]

    def CalculateOptionValue(self, current_price):
        s = Stats()
        pop = s.CalculatePoP(current_price)[0]
        return (1.0 - pop) * 0.01

if __name__ == "__main__":
    real_time = "-rt" in sys.argv
    at = AutoTrader(real_time)
    stop = False
    while not stop:
        try:
            # Wait for next round and get some critical information.
            print("Sleeping until next round begins...")
            at.SleepToExpiry()
            current_price = at.GetCurrentPrice()

            # Check last round's trade to see if it won or not.
            if len(at.open_orders) > 0:
                strike = float(at.open_orders[0][0]["strike"])
                if current_price >= strike:
                    if not real_time:
                        at.balance -= 0.01
                    print("LOSE\tBalance => {0}").format(at.balance)
                else:
                    print("WIN\tBalance => {0}").format(at.balance)
                at.open_orders.pop(0)

            # Continue with our previously scheduled programming.
            time.sleep(5)
            attempts = 3
            if at.balance <= 0:
                print("The rum's gone, mate! No yacht for you...")
                attempts = 0
                stop = True
            while attempts > 0:
                strike, price_list = at.GetOptionPrices()
                if len(price_list) > 0:
                    if float(price_list[0]["price"]) > at.CalculateOptionValue(current_price):
                        print("{0} => {1}").format(
                            current_price,
                            at.CalculateOptionValue(current_price)
                        )
                        at.open_orders.append(
                            at.OpenOrder(
                                at.GetNearestExpiry(),
                                at.GetUpperBound(current_price),
                                max(1, int(at.balance)),
                                price_list[0]["price"]
                            )
                        )
                        print("ORDER {0} => {1} @ {2} strike <=").format(
                            current_price,
                            price_list[0]["price"],
                            strike
                        )
                        attempts = 0
                else:
                    print("No open bids for {1} strike...").format(strike)
                attempts -= 1
                if attempts > 0:
                    time.sleep(10)
        except KeyboardInterrupt:
            print("Detected keyboard interrupt. Stopping program...")
            stop = True
    if real_time:
        at.balance = at.GetBTCBalance()
    print("Final balance => {0} BTC").format(at.balance)
