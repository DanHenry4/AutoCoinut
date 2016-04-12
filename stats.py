from manager import Manager
import csv
import math
import sys
import time

class Stats(Manager):
    def __init__(self):
        Manager.__init__(self)
        self.data = self.ReadData()

    # ReadData() returns all recorded data in list format.
    def ReadData(self):
        with open(self.path + self.file_name, "rb") as f:
            reader = csv.reader(f)
            return list(reader)

    # CalculatePoP() returns the probability that a trade will win,
    # given the current and historical price of BTC.
    # value is the current price of BTC.
    def CalculatePoP(self, value):
        n = 0
        d = 0
        value_cent = int((float(value) * 100) % 10)
        for i in range(len(self.data) - 1):
            # 300 seconds == 5 minutes. If ex2 - ex1 != 300, then
            # the expiry times are from different recordings.
            ex1 = int(self.data[i][0])
            ex2 = int(self.data[i + 1][0])
            data_cent = int((float(self.data[i][1]) * 100) % 10)
            if ex2 - ex1 == 300 and data_cent == value_cent:
                p1, p2 = self.GetPriceTuple(self.data[i][0])
                if p2 < self.GetUpperBound(p1):
                    n += 1
                d += 1
        return (float(n) / d, d)

    # GetPriceTuple returns a tuple of:
    #   price[expiry_time]
    #   price[expiry_time + 1]
    def GetPriceTuple(self, expiry_time):
        expiry_index = self.GetItemIndex(expiry_time)
        p1 = float(self.data[expiry_index][1])
        p2 = float(self.data[expiry_index + 1][1])
        return (p1, p2)

    # GetItemIndex() returns the index that a list with an item appears in a list.
    def GetItemIndex(self, item):
        for i in range(len(self.data)):
            if item in self.data[i]:
                return i

if __name__ == "__main__":
    s = Stats()

    # Record statistics.
    if "-s" in sys.argv:
        while True:
            nearest_expiry = s.GetNearestExpiry()
            s.SleepToExpiry()
            s.RecordExpiryPrice(nearest_expiry)
            time.sleep(5)

    # Calculate the probability of profit for each cent value.
    elif "-p" in sys.argv:
        count = 0
        for i in range(10):
            pop, n = s.CalculatePoP(i / 100.0)
            count += n
            print("\t{0} -> {1:.2f}% \t[n={2}]").format(i, pop * 100, n)
        print("\tTOTAL\t\t[n={0}]").format(count)
