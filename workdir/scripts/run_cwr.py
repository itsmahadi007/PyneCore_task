"""@pyne"""
from pynecore import Series
from pynecore.lib import script, high, low, plot, color
from pynecore.lib.ta import sma
from pynecore.core.ohlcv_file import OHLCVReader
from pathlib import Path
import json
import csv
from typing import List, Dict, Any


@script.indicator(title="Candle Widening Ratio (CWR)", overlay=False)
def main(
        length=20,
):
    """Calculate Candle Widening Ratio using PyneCore"""
    # Calculate current candle range
    current_range = high - low

    # Calculate average range over the last N candles using PyneCore's SMA
    average_range = sma(current_range, length)

    # Calculate CWR (avoid division by zero)
    try:
        cwr = current_range / average_range
    except (ZeroDivisionError, TypeError):
        cwr = 0

    # Plot the results
    plot(cwr, "CWR", color=color.blue)
    plot(1.0, "Baseline", color=color.gray)

    return {"cwr": cwr, "baseline": 1.0}


def load_ohlcv_with_pynecore(file_path: str) -> List[Dict[str, Any]]:
    """Load OHLCV data using PyneCore's OHLCVReader"""
    data = []
    
    with OHLCVReader(Path(file_path)) as reader:
        for candle in reader:
            data.append({
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            })
    
    return data


def calculate_cwr_standalone(ohlcv_data: List[Dict[str, Any]], length: int = 20) -> List[Dict[str, Any]]:
    """Calculate CWR for standalone execution"""
    results = []
    
    # Calculate ranges for all candles
    ranges = [candle['high'] - candle['low'] for candle in ohlcv_data]
    
    # Calculate SMA of ranges manually for standalone mode
    average_ranges = []
    for i in range(len(ranges)):
        if i < length - 1:
            # Not enough data for full SMA, use available data
            window = ranges[:i+1]
        else:
            # Use full window
            window = ranges[i-length+1:i+1]
        
        average_ranges.append(sum(window) / len(window))
    
    # Calculate CWR for each candle
    for i, (current_range, avg_range) in enumerate(zip(ranges, average_ranges)):
        try:
            cwr = current_range / avg_range if avg_range != 0 else 0
        except (ZeroDivisionError, TypeError):
            cwr = 0
        
        results.append({
            'timestamp': ohlcv_data[i]['timestamp'],
            'open': ohlcv_data[i]['open'],
            'high': ohlcv_data[i]['high'],
            'low': ohlcv_data[i]['low'],
            'close': ohlcv_data[i]['close'],
            'volume': ohlcv_data[i]['volume'],
            'current_range': current_range,
            'average_range': avg_range,
            'cwr': cwr,
            'baseline': 1.0
        })
    
    return results


def save_results_json(results: List[Dict[str, Any]], output_path: str):
    """Save results to JSON file"""
    with open(output_path, 'w') as f:
        json.dump({
            'indicator': 'Candle Widening Ratio (CWR)',
            'description': 'Measures how the current candle\'s range compares to the average range of previous candles',
            'calculation': 'current_range / average_range where current_range = high - low',
            'data_points': len(results),
            'results': results
        }, f, indent=2)


def save_results_csv(results: List[Dict[str, Any]], output_path: str):
    """Save results to CSV file"""
    if not results:
        return
    
    fieldnames = results[0].keys()
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def run_standalone():
    """Standalone function to run CWR calculation with file output"""
    # Set up paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    output_dir = script_dir.parent / 'output'
    
    # Input and output files
    input_file = data_dir / 'ccxt_BYBIT_BTC_USDT_USDT_1D.ohlcv'
    output_json = output_dir / 'cwr_results.json'
    output_csv = output_dir / 'cwr_results.csv'
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    print("=== Candle Widening Ratio (CWR) Indicator ===")
    print(f"Loading data from: {input_file}")
    
    # Load OHLCV data using PyneCore's reader
    ohlcv_data = load_ohlcv_with_pynecore(str(input_file))
    print(f"Loaded {len(ohlcv_data)} candles")
    
    # Calculate CWR
    print("Calculating CWR...")
    cwr_results = calculate_cwr_standalone(ohlcv_data, length=20)
    
    # Save results
    print(f"Saving results to: {output_json}")
    save_results_json(cwr_results, str(output_json))
    
    print(f"Saving results to: {output_csv}")
    save_results_csv(cwr_results, str(output_csv))
    
    # Print some statistics
    if cwr_results:
        cwr_values = [r['cwr'] for r in cwr_results if r['cwr'] > 0]
        if cwr_values:
            print(f"\nCWR Statistics:")
            print(f"  Total candles: {len(cwr_results)}")
            print(f"  Valid CWR values: {len(cwr_values)}")
            print(f"  Average CWR: {sum(cwr_values) / len(cwr_values):.4f}")
            print(f"  Min CWR: {min(cwr_values):.4f}")
            print(f"  Max CWR: {max(cwr_values):.4f}")
    
    print("\n✅ CWR calculation completed successfully!")


if __name__ == '__main__':
    # Run in standalone mode for file output
    run_standalone()