"""
@pyne
"""
from pynecore import Series
from pynecore.lib import script, high, low, close, open, volume, plot, color
from pynecore.lib.ta import sma, ema, rsi  # Technical analysis functions

@script.indicator(title="My Indicator", overlay=False)
def main(
    length=20,  # Use simple parameters, avoid input.int() with validation
):
    """Your indicator logic here"""

    # 1. Calculate your indicator
    my_value = close - sma(close, length)

    # 2. Handle edge cases
    try:
        ratio = my_value / close
    except (ZeroDivisionError, TypeError):
        ratio = 0

    # 3. Plot results
    plot(my_value, "My Value", color=color.blue)
    plot(0, "Zero Line", color=color.gray)

    # 4. Return dictionary (REQUIRED)
    return {
        "my_value": my_value,
        "ratio": ratio
    }