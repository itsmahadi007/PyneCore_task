"""
@pyne
"""
from pynecore.lib import script, high, low, plot

@script.indicator(title="Debug Test")
def main():
    print("Debug Test")
    range_val = high - low
    plot(range_val, "Range")
    print(range_val)
    return {"range": range_val}

