from pathlib import Path
from datetime import datetime
import sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pynecore.core.ohlcv_file import OHLCVReader
from pynecore.core.syminfo import SymInfo
from pynecore.core.script_runner import ScriptRunner

def run_cwr_programmatically():
    """Run the CWR indicator programmatically using PyneCore's core components"""
    
    # Define paths (similar to CLI app_state)
    workdir = Path("workdir").resolve()
    scripts_dir = workdir / "scripts"
    data_dir = workdir / "data"
    output_dir = workdir / "output"
    
    # Script and data paths
    script_path = scripts_dir / "run_cwr.py"
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
            print(f"  Strategy stats: {strat_path}")
            print(f"  Equity curve: {equity_path}")
            
            # Generate visualization
            chart_path = create_cwr_visualization(plot_path, output_dir)
            print(f"  Visualization: {chart_path}")
            
        finally:
            # Remove lib directory from Python path
            if lib_path_added:
                sys.path.remove(str(lib_dir))

def create_cwr_visualization(csv_path: Path, output_dir: Path) -> Path:
    """Create an interactive visualization of price data with CWR overlay"""
    
    # Read the CSV data
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'])
    
    # Filter out rows where CWR is NaN (initial period before SMA calculation)
    df_with_cwr = df.dropna(subset=['cwr'])
    
    # Create subplots: price chart on top, CWR indicator below
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('BTC/USDT Price Chart', 'Candle Widening Ratio (CWR)'),
        row_heights=[0.7, 0.3]
    )
    
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
    
    # Add CWR line chart
    fig.add_trace(
        go.Scatter(
            x=df_with_cwr['time'],
            y=df_with_cwr['cwr'],
            mode='lines',
            name='CWR',
            line=dict(color='#2E86AB', width=2)
        ),
        row=2, col=1
    )
    
    # Add horizontal reference lines for CWR
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray", 
                  annotation_text="Baseline (1.0)", row=2, col=1)
    fig.add_hline(y=1.5, line_dash="dot", line_color="red", 
                  annotation_text="High Volatility (1.5)", row=2, col=1)
    fig.add_hline(y=0.5, line_dash="dot", line_color="green", 
                  annotation_text="Low Volatility (0.5)", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'BTC/USDT Price Chart with Candle Widening Ratio (CWR) Indicator',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Date',
        yaxis_title='Price (USDT)',
        yaxis2_title='CWR Value',
        height=800,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Update x-axis formatting
    fig.update_xaxes(rangeslider_visible=False)
    
    # Save the chart
    chart_path = Path('visualize_html_file') / 'cwr_visualization.html'
    # Create directory if it doesn't exist
    Path('visualize_html_file').mkdir(parents=True, exist_ok=True)
    fig.write_html(str(chart_path))
    
    return chart_path

if __name__ == "__main__":
    run_cwr_programmatically()