#!/usr/bin/env python3
"""
Script to run the Candle Widening Ratio (CWR) indicator using PyneCore
and save the results to a file.
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_cwr_indicator():
    """Run the CWR indicator and save results to file"""
    
    # Set up paths
    workdir = Path("workdir")
    script_path = workdir / "scripts" / "run_cwr.py"
    data_path = workdir / "data" / "ccxt_BYBIT_BTC_USDT_USDT_1D.ohlcv"
    output_dir = workdir / "output"
    output_file = output_dir / "cwr_results.json"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Running CWR indicator...")
    print(f"Script: {script_path}")
    print(f"Data: {data_path}")
    print(f"Output will be saved to: {output_file}")
    
    try:
        # Change to workdir and run the PyneCore command
        os.chdir(workdir)
        
        # Run the PyneCore command using uv
        cmd = [
            "uv", "run", "python", "-m", "pynecore", "run", 
            str(script_path.relative_to(workdir)), 
            str(data_path.relative_to(workdir))
        ]
        
        print(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Command executed successfully!")
        print(f"Output: {result.stdout}")
        
        if result.stderr:
            print(f"Warnings/Errors: {result.stderr}")
        
        # Create a summary of the results
        results_summary = {
            "indicator": "Candle Widening Ratio (CWR)",
            "script_path": str(script_path),
            "data_path": str(data_path),
            "execution_status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "description": "CWR measures how the current candle's range compares to the average range of previous candles",
            "calculation": "current_range / average_range where current_range = high - low"
        }
        
        # Change back to original directory
        os.chdir('..')
        
        # Ensure output directory exists again (after changing back)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save results to JSON file
        with open(output_file, 'w') as f:
            json.dump(results_summary, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running PyneCore command: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        
        # Change back to original directory
        os.chdir('..')
        
        # Ensure output directory exists again (after changing back)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save error information
        error_summary = {
            "indicator": "Candle Widening Ratio (CWR)",
            "script_path": str(script_path),
            "data_path": str(data_path),
            "execution_status": "error",
            "error_code": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr
        }
        
        with open(output_file, 'w') as f:
            json.dump(error_summary, f, indent=2)
        
        return False
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        
        # Try to change back to original directory
        try:
            os.chdir('..')
        except:
            pass
            
        return False

if __name__ == "__main__":
    print("=== Candle Widening Ratio (CWR) Indicator Runner ===")
    print()
    
    success = run_cwr_indicator()
    
    if success:
        print("\n✅ CWR indicator executed successfully!")
        print("Check the output directory for results.")
    else:
        print("\n❌ Failed to execute CWR indicator.")
        print("Check the error messages above.")
    
    sys.exit(0 if success else 1)