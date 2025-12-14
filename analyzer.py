import time, statistics

#1 rate

def compute_rate(events, now, window):
    return sum(
        e.value for e in events
        if now - e.timestamp <= window
    ) / window


#2 adaptive threshold

def compute_threshold(rates):
    if len(rates) < 5:
        return float("inf")
    mean = statistics.mean(rates)
    std = statistics.pstdev(rates)
    return mean + 2 * std


#3 machine for burst detection
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
