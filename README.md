# CWR (Candle Widening Ratio) Indicator Project

This project implements a Candle Widening Ratio (CWR) indicator using PyneCore, a Python framework for technical analysis and trading strategy development.

## Original Task Requirements

This project was created to fulfill the following requirements:

**Create an indicator in PyneCore called Candle Widening Ratio (CWR)**, which measures how the current candle's range (high - low) compares to the average range of the previous candles.

**Calculation:**
- Current candle range: `high - low`
- Average range of the last N candles (e.g. N = 20): average of `(high - low)` over the past N candles
- Final value: `current range / average range`

**Example:** If the current candle is 2 units tall, and the previous 20 candles' average is 1.5, then: `2 / 1.5 = 1.33`

**Requirements:**
- ✅ Write a PyneCore script that calculates this indicator
- ✅ Load OHLCV data (using PyneCore's optimized ohlcv format)
- ✅ Run the script using Python code (programmatic execution, not CLI)
- ✅ Save the result into a file (CSV format)
- ✅ **Optional:** Add visualization using Plotly (interactive chart overlay)

## What is CWR?

The Candle Widening Ratio (CWR) is a volatility indicator that measures the current candle's range relative to the average range over a specified period. It helps identify periods of high or low volatility in price movements.

- **CWR > 1.0**: Current volatility is above average
- **CWR = 1.0**: Current volatility equals the average (baseline)
- **CWR < 1.0**: Current volatility is below average


## How to Download Example Data

To download 30 days of daily BTC/USDT data from Bybit using PyneCore's CLI, run the following command:

```
uv run pyne data download ccxt --symbol "BYBIT:BTC/USDT:USDT" --timeframe 1D --from 30
```

This command will save the `.ohlcv` and `.toml` files in the correct location (`workdir/data/`).

## Project Structure

```
PyneCore_task/
├── README.md
├── run_cwr_programmatic.py          # Programmatic execution script
├── visualize_html_file/              # Visualization output directory
│   └── cwr_visualization.html        # Interactive chart (generated after running)
└── workdir/
    ├── scripts/
    │   └── run_cwr.py                # CWR indicator implementation
    ├── data/ 
    │   ├── ccxt_BYBIT_BTC_USDT_USDT_1D.ohlcv  # OHLCV data file
    │   └── ccxt_BYBIT_BTC_USDT_USDT_1D.toml   # Symbol information
    └── output/                       # Results output directory
        └── run_cwr.csv              # Main indicator data with CWR values
```


## Installation

### Install uv (if not already installed)

First, install the `uv` package manager:

**Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Project Dependencies

Once `uv` is installed, run this command in the project directory to install all required packages:

```bash
uv sync
```

This will automatically install all dependencies defined in `pyproject.toml`.



## How to Run

### Method 1: CLI Execution (PyneCore Command)

Run the CWR indicator using PyneCore's command-line interface:

```bash
pyne run workdir/scripts/run_cwr.py workdir/data/ccxt_BYBIT_BTC_USDT_USDT_1D.ohlcv
```

This will:
- Execute the CWR indicator script
- Process the BTC/USDT daily OHLCV data
- Save results to `workdir/output/` directory

### Method 2: Programmatic Execution (Recommended)

Run the CWR indicator programmatically with enhanced features:

```bash
uv run python run_cwr_programmatic.py
```

This method provides:
- Same functionality as CLI execution
- **Automatic interactive visualization generation**
- Better error handling and progress feedback
- Programmatic access to PyneCore's core components

## Output Files

### Standard Output (Both Methods)

After running either method, you'll find the following file in `workdir/output/`:

- **`run_cwr.csv`**: Main results containing OHLCV data with CWR values, current range, average range, and baseline reference

### Visualization Output (Programmatic Method Only)

When using the programmatic method, an interactive HTML chart is generated:

**Location**: `g:\Coding\PyneCore_task\visualize_html_file\cwr_visualization.html`

This visualization includes:
- **Upper Panel**: BTC/USDT candlestick price chart
- **Lower Panel**: CWR indicator line with reference levels:
  - Gray dashed line (1.0): Baseline - average volatility
  - Red dotted line (1.5): High volatility threshold
  - Green dotted line (0.5): Low volatility threshold
- **Interactive Features**: Zoom, pan, hover tooltips, and time range selection

## Understanding the Results

### CSV Data Columns

- `time`: Timestamp for each data point
- `open`, `high`, `low`, `close`: OHLCV price data
- `volume`: Trading volume
- `cwr`: Candle Widening Ratio value
- `baseline`: Reference line (always 1.0)
- `current_range`: Current candle's high-low range
- `average_range`: 20-period simple moving average of ranges

### Interpreting CWR Values

- **CWR > 1.5**: Exceptionally high volatility period
- **1.0 < CWR < 1.5**: Above-average volatility
- **CWR ≈ 1.0**: Normal/average volatility
- **0.5 < CWR < 1.0**: Below-average volatility
- **CWR < 0.5**: Very low volatility period

## Customization

You can modify the CWR calculation by editing `workdir/scripts/run_cwr.py`:

- Change the `length` parameter (default: 20) to adjust the moving average period
- Modify reference levels for different volatility thresholds
- Add additional technical indicators or analysis

## Troubleshooting

1. **File not found errors**: Ensure all required files exist in the `workdir` structure
2. **Module import errors**: Install missing dependencies with `uv add` or `pip install`
3. **Permission errors**: Check file/directory permissions
4. **Data format issues**: Verify OHLCV data file format and corresponding .toml file

## Example Output

After successful execution, you should see output similar to:

```
Running script: run_cwr.py
Data: ccxt_BYBIT_BTC_USDT_USDT_1D.ohlcv

PyneCore script executed successfully!
Results saved to:
  Plot data: workdir\output\run_cwr.csv
  Visualization: visualize_html_file\cwr_visualization.html
```

## Next Steps

1. Open the generated HTML visualization in your browser
2. Analyze the CWR patterns in relation to price movements
3. Use the CSV data for further analysis or strategy development
4. Experiment with different parameters or additional indicators