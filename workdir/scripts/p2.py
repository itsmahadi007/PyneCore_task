"""
@pyne

This code was compiled by PyneComp — the Pine Script to Python compiler.
Accessible via PyneSys: https://pynesys.io
Run with open-source PyneCore: https://pynecore.org
"""
from pynecore.lib import close, color, location, plot, plotshape, script, shape, size, ta


@script.indicator("My script", overlay=True)
def main():
    ma1 = ta.sma(close, 20)
    plot(ma1, color=color.blue)

    ma2 = ta.sma(close, 10)
    plot(ma2, color=color.yellow)

    buy = ta.crossover(ma2, ma1)
    sell = ta.crossunder(ma2, ma1)

    plotshape(buy, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
    plotshape(sell, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
