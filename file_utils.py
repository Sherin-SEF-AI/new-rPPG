"""
File Utilities Module
Utility functions for file operations and data export.
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional


def save_data(data: Dict[str, Any], file_path: str, format: str = 'auto') -> bool:
    """
    Save data to file in various formats.
    
    Args:
        data: Data dictionary to save
        file_path: Output file path
        format: File format ('csv', 'json', 'auto')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Determine format from file extension if auto
        if format == 'auto':
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                format = 'csv'
            elif ext == '.json':
                format = 'json'
            else:
                format = 'json'  # Default
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if format == 'csv':
            return save_csv(data, file_path)
        elif format == 'json':
            return save_json(data, file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    except Exception as e:
        print(f"Error saving data: {e}")
        return False


def save_csv(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to CSV file."""
    try:
        # Convert data to DataFrame-friendly format
        df_data = {}
        
        for key, value in data.items():
            if isinstance(value, list):
                # Pad lists to same length
                max_len = max(len(v) if isinstance(v, list) else 1 for v in data.values())
                padded_value = value + [None] * (max_len - len(value))
                df_data[key] = padded_value
            else:
                df_data[key] = [value]
        
        df = pd.DataFrame(df_data)
        df.to_csv(file_path, index=False)
        return True
        
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to JSON file."""
    try:
        # Convert numpy arrays to lists for JSON serialization
        json_data = convert_for_json(data)
        
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        return True
        
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def convert_for_json(obj: Any) -> Any:
    """Convert object to JSON-serializable format."""
    if isinstance(obj, dict):
        return {key: convert_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_json(item) for item in obj]
    elif hasattr(obj, 'tolist'):  # numpy arrays
        return obj.tolist()
    elif hasattr(obj, '__dict__'):  # custom objects
        return str(obj)
    else:
        return obj


def load_data(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from file.
    
    Args:
        file_path: Input file path
        
    Returns:
        Loaded data dictionary or None if failed
    """
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.csv':
            return load_csv(file_path)
        elif ext == '.json':
            return load_json(file_path)
        else:
            print(f"Unsupported file format: {ext}")
            return None
            
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def load_csv(file_path: str) -> Optional[Dict[str, Any]]:
    """Load data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('list')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None


def export_results(results: Dict[str, Any], output_dir: str, 
                  base_name: str = "rppg_results") -> str:
    """
    Export results to multiple formats.
    
    Args:
        results: Results dictionary
        output_dir: Output directory
        base_name: Base name for output files
        
    Returns:
        Path to the created files
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to JSON
        json_path = os.path.join(output_dir, f"{base_name}_{timestamp}.json")
        save_json(results, json_path)
        
        # Export to CSV
        csv_path = os.path.join(output_dir, f"{base_name}_{timestamp}.csv")
        save_csv(results, csv_path)
        
        # Create summary report
        summary_path = os.path.join(output_dir, f"{base_name}_{timestamp}_summary.txt")
        create_summary_report(results, summary_path)
        
        return output_dir
        
    except Exception as e:
        print(f"Error exporting results: {e}")
        return ""


def create_summary_report(results: Dict[str, Any], file_path: str) -> bool:
    """Create a human-readable summary report."""
    try:
        with open(file_path, 'w') as f:
            f.write("rPPG Analysis Summary Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Heart rate statistics
            if 'heart_rates' in results:
                hr_data = results['heart_rates']
                if hr_data:
                    f.write("Heart Rate Statistics:\n")
                    f.write(f"  Mean: {sum(hr_data)/len(hr_data):.1f} BPM\n")
                    f.write(f"  Min: {min(hr_data):.1f} BPM\n")
                    f.write(f"  Max: {max(hr_data):.1f} BPM\n")
                    f.write(f"  Total measurements: {len(hr_data)}\n\n")
            
            # Quality metrics
            if 'quality_metrics' in results:
                f.write("Quality Metrics:\n")
                for key, value in results['quality_metrics'].items():
                    if isinstance(value, float):
                        f.write(f"  {key}: {value:.3f}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
                f.write("\n")
            
            # HRV metrics
            if 'hrv_metrics' in results:
                f.write("HRV Metrics:\n")
                for key, value in results['hrv_metrics'].items():
                    if isinstance(value, float):
                        f.write(f"  {key}: {value:.3f}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
                f.write("\n")
            
            # Processing information
            if 'processing_info' in results:
                f.write("Processing Information:\n")
                for key, value in results['processing_info'].items():
                    f.write(f"  {key}: {value}\n")
        
        return True
        
    except Exception as e:
        print(f"Error creating summary report: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0


def validate_file_path(file_path: str) -> bool:
    """Validate if file path is accessible."""
    try:
        # Check if directory exists
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            return False
        
        # Check if file exists (for reading)
        if os.path.exists(file_path):
            return os.access(file_path, os.R_OK)
        
        # Check if directory is writable (for writing)
        if dir_path:
            return os.access(dir_path, os.W_OK)
        
        return True
        
    except:
        return False 