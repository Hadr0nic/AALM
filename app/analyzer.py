import time, statistics

'''
1. rate (per second)

calculates the current load, sums the value of all events occurring
within the last window seconds (default 60s) and divides by the window size.
'''

def compute_rate(events, now, window):
    return sum(
        value for (timestamp, value) in events
        if now - timestamp <= window
    ) / window

'''
2. adaptive threshold

 by looking at the history of calculated rates, compute_threshold determines what constitutes an "abnormal" rate.
 if there are fewer than 5 data points, it returns infinity (no detection).
 otherwise, it calculates the mean and standard deviation (pstdev).
 the threshold is set to Mean + 2 StdDev (inspired by Z-score approach)
 if the current rate exceeds this dynamic threshold, it is considered anomalous.
'''
def compute_threshold(rates):
    if len(rates) < 5:
        return float("inf")
    mean = statistics.mean(rates)
    std = statistics.pstdev(rates)
    return mean + 2 * std


#3 burst detection (as a machine)
class BurstDetector:
    def __init__(self):
        self.current_burst = None
        self.recent_rates = []

    def update(self, rate, threshold, now):
        self.recent_rates.append(rate)
        if len(self.recent_rates) > 100:
            self.recent_rates.pop(0)

        if rate > threshold:
            if self.current_burst is None:
                self.current_burst = {
                    "start": now,
                    "events": 0,
                    "peak": rate
                }
            self.current_burst["events"] += rate
            self.current_burst["peak"] = max(
                self.current_burst["peak"], rate
            )
            return None

        if self.current_burst is not None:
            burst = self.current_burst
            self.current_burst = None
            return burst

        return None
