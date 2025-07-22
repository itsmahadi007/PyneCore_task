"""
@pyne

This code was compiled by PyneComp — the Pine Script to Python compiler.
Accessible via PyneSys: https://pynesys.io
Run with open-source PyneCore: https://pynecore.org
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("Moving Average Crossover - Actually Works", overlay=True)
def main(
    fastLength=input(9, title="Fast MA Length"),
    slowLength=input(21, title="Slow MA Length")
):

    fastMA = ta.sma(close, fastLength)
    slowMA = ta.sma(close, slowLength)

    plot(fastMA, color=color.green, title='Fast MA', linestyle="--")
    plot(slowMA, color=color.red, title='Slow MA', linestyle=":")

    if ta.crossover(fastMA, slowMA):
        strategy.entry('Long', strategy.long)

    if ta.crossunder(fastMA, slowMA):
        strategy.close('Long')
