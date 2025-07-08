from pathlib import Path
from datetime import datetime
import sys

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
            
        finally:
            # Remove lib directory from Python path
            if lib_path_added:
                sys.path.remove(str(lib_dir))

if __name__ == "__main__":
    run_cwr_programmatically()