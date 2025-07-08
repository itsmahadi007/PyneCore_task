"""@pyne"""
from pynecore.lib import script, high, low, color, plot
from pynecore.lib.ta import sma

@script.indicator(title="Candle Widening Ratio (CWR)", overlay=True)
def main(length: int = 20):
    current_range = high - low
    average_range = sma(current_range, length)
    cwr = current_range / average_range
    plot(1.0, "Baseline", color=color.gray, linestyle="--")
    plot(1.5, "High Volatility", color=color.red, linestyle=":")
    plot(0.5, "Low Volatility", color=color.green, linestyle=":")
    return {
        "cwr": cwr,
        "baseline": 1.0,
        "current_range": current_range,
        "average_range": average_range
    }
