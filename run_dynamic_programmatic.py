from pathlib import Path
from datetime import datetime
import sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pynecore.core.ohlcv_file import OHLCVReader
from pynecore.core.syminfo import SymInfo
from pynecore.core.script_runner import ScriptRunner

# Global configuration
FILE_NAME = "p2"
CHART_FILENAME = f"{FILE_NAME}_visualization.html"
SCRIPT_NAME = f"{FILE_NAME}.py"

def run_cwr_programmatically():
    """Run the CWR indicator programmatically using PyneCore's core components"""
    
    # Define paths (similar to CLI app_state)
    workdir = Path("workdir").resolve()
    scripts_dir = workdir / "scripts"
    data_dir = workdir / "data"
    output_dir = workdir / "output"
    
    # Script and data paths
    script_path = scripts_dir / SCRIPT_NAME
    data_path = data_dir / "ccxt_BYBIT_BTC_USDT_USDT_1D.ohlcv"
    
    # Output paths (following CLI naming convention)
    plot_path = output_dir / f"{script_path.stem}.csv"
    strat_path = output_dir / f"{script_path.stem}_strat.csv"
    equity_path = output_dir / f"{script_path.stem}_equity.csv"
    
    # Validate files exist
    if not script_path.exists():
        raise FileNotFoundError(f"Script file '{script_path}' not found!")
    if not data_path.exists():
        raise FileNotFoundError(f"Data file '{data_path}' not found!")
    
    # Load symbol info
    try:
        syminfo = SymInfo.load_toml(data_path.with_suffix(".toml"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Symbol info file '{data_path.with_suffix('.toml')}' not found!")
    
    # Open data file and run script
    with OHLCVReader(data_path) as reader:
        # Use full time range from data
        time_from = reader.start_datetime.replace(tzinfo=None)
        time_to = reader.end_datetime.replace(tzinfo=None)
        
        # Get data iterator and size
        size = reader.get_size(int(time_from.timestamp()), int(time_to.timestamp()))
        ohlcv_iter = reader.read_from(int(time_from.timestamp()), int(time_to.timestamp()))
        
        # Add lib directory to Python path for library imports (like CLI does)
        lib_dir = scripts_dir / "lib"
        lib_path_added = False
        if lib_dir.exists() and lib_dir.is_dir():
            sys.path.insert(0, str(lib_dir))
            lib_path_added = True
        
        try:
            # Create and run script runner
            runner = ScriptRunner(
                script_path, 
                ohlcv_iter, 
                syminfo, 
                last_bar_index=size - 1,
                plot_path=plot_path, 
                strat_path=strat_path, 
                equity_path=equity_path
            )
            
            print(f"Running script: {script_path.name}")
            print(f"Data: {data_path.name}")
            print(f"Time range: {time_from} to {time_to}")
            
            # Run the script
            runner.run()
            
            print("\nPyneCore script executed successfully!")
            print(f"Results saved to:")
            print(f"  Plot data: {plot_path}")
            
            # Generate visualization
            chart_path = create_dynamic_visualization(plot_path, output_dir)
            print(f"  Visualization: {chart_path}")
            
        finally:
            # Remove lib directory from Python path
            if lib_path_added:
                sys.path.remove(str(lib_dir))

def create_dynamic_visualization(csv_path: Path, output_dir: Path) -> Path:
    """Create an interactive visualization of price data with dynamic indicator overlay"""
    
    # Read the CSV data
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'])
    
    # Identify OHLCV columns
    ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
    
    # Identify indicator columns (non-OHLCV, non-time columns)
    indicator_cols = [col for col in df.columns if col not in ohlcv_cols + ['time']]
    
    # Detect signal columns (typically binary 0/1 values for buy/sell signals)
    signal_cols = []
    line_indicator_cols = []
    
    # Analyze indicator columns to separate signals from continuous indicators
    for col in indicator_cols:
        # Check if column contains mostly NaN/0 values with occasional 1s (typical for signals)
        non_na_values = df[col].dropna()
        if len(non_na_values) > 0:
            unique_vals = non_na_values.unique()
            # If column has binary values or very few unique values, treat as signal
            if set(unique_vals).issubset({0, 1}) or (len(unique_vals) <= 3 and non_na_values.max() <= 1):
                signal_cols.append(col)
            else:
                line_indicator_cols.append(col)
        else:
            line_indicator_cols.append(col)
    
    # Filter out rows with NaN values in indicator columns for line charts
    if line_indicator_cols:
        df_with_indicators = df.dropna(subset=line_indicator_cols)
    else:
        df_with_indicators = df
    
    # Determine if we need subplots based on available indicators
    if line_indicator_cols:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('BTC/USDT Price Chart', f'Indicators ({', '.join(line_indicator_cols)})'),
            row_heights=[0.7, 0.3]
        )
        indicator_row = 2
    else:
        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=('BTC/USDT Price Chart',)
        )
        indicator_row = 1
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='BTC/USDT',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ),
        row=1, col=1
    )
    
    # Add indicator lines if available
    if line_indicator_cols:
        colors = ['#2E86AB', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        for i, col in enumerate(line_indicator_cols):
            color = colors[i % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=df_with_indicators['time'],
                    y=df_with_indicators[col],
                    mode='lines',
                    name=col,
                    line=dict(color=color, width=2)
                ),
                row=indicator_row, col=1
            )
    
    # Add buy/sell signals if detected
    for col in signal_cols:
        # Get non-NaN signal points
        signal_df = df[df[col].notna() & (df[col] != 0)]
        
        if not signal_df.empty:
            # Determine if this is likely a buy or sell signal based on column name
            is_buy_signal = any(term in col.lower() for term in ['buy', 'long', 'up'])
            is_sell_signal = any(term in col.lower() for term in ['sell', 'short', 'down'])
            
            # Default to buy signal if can't determine
            if not (is_buy_signal or is_sell_signal):
                is_buy_signal = True
            
            # Set marker properties based on signal type
            if is_buy_signal:
                marker_color = 'green'
                marker_symbol = 'triangle-up'
                marker_size = 10
                signal_name = f"Buy Signal ({col})"
                # Position below candle
                y_values = signal_df['low'] * 0.995  # Slightly below the low price
            else:  # sell signal
                marker_color = 'red'
                marker_symbol = 'triangle-down'
                marker_size = 10
                signal_name = f"Sell Signal ({col})"
                # Position above candle
                y_values = signal_df['high'] * 1.005  # Slightly above the high price
            
            # Add the signal markers
            fig.add_trace(
                go.Scatter(
                    x=signal_df['time'],
                    y=y_values,
                    mode='markers',
                    name=signal_name,
                    marker=dict(
                        color=marker_color,
                        size=marker_size,
                        symbol=marker_symbol
                    )
                ),
                row=1, col=1
            )
    
    # Add reference lines for specific indicators
    if 'cwr' in line_indicator_cols:
        fig.add_hline(y=1.0, line_dash="dash", line_color="gray", 
                      annotation_text="Baseline (1.0)", row=indicator_row, col=1)
        fig.add_hline(y=1.5, line_dash="dot", line_color="red", 
                      annotation_text="High Volatility (1.5)", row=indicator_row, col=1)
        fig.add_hline(y=0.5, line_dash="dot", line_color="green", 
                      annotation_text="Low Volatility (0.5)", row=indicator_row, col=1)
    
    # Determine chart title based on indicators and script name
    script_name = csv_path.stem
    
    if 'cwr' in line_indicator_cols:
        chart_title = f'{script_name} - BTC/USDT with Candle Widening Ratio (CWR) Indicator'
        indicator_title = 'CWR Value'
    elif line_indicator_cols:
        chart_title = f'{script_name} - BTC/USDT with {', '.join(line_indicator_cols)} Indicators'
        indicator_title = 'Indicator Values'
    else:
        chart_title = f'{script_name} - BTC/USDT Price Chart'
        indicator_title = ''
    
    # Add signal information to title if present
    if signal_cols:
        chart_title += f" and {len(signal_cols)} Trading Signals"
    
    # Update layout
    layout_config = {
        'title': {
            'text': chart_title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        'xaxis_title': 'Date',
        'yaxis_title': 'Price (USDT)',
        'height': 800,
        'showlegend': True,
        'hovermode': 'x unified',
        'template': 'plotly_white'
    }
    
    if line_indicator_cols:
        layout_config['yaxis2_title'] = indicator_title
    
    fig.update_layout(**layout_config)
    
    # Update x-axis formatting
    fig.update_xaxes(rangeslider_visible=False)
    
    # Save the chart
    chart_path = Path('visualize_html_file') / CHART_FILENAME
    # Create directory if it doesn't exist
    Path('visualize_html_file').mkdir(parents=True, exist_ok=True)
    fig.write_html(str(chart_path))
    
    return chart_path

if __name__ == "__main__":
    run_cwr_programmatically()