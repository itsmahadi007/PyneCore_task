"""
@pyne
"""
from pynecore.lib import script, high, low, plot

@script.indicator(title="Debug Test")
def main():
    range_val = high - low
    plot(range_val, "Range")
    return {"range": range_val}
