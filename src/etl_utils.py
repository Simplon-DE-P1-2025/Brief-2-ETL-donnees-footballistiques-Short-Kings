"""
Utility functions for ETL operations on football data.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any


def load_csv_data(filepath: str) -> pd.DataFrame:
    """
    Load data from a CSV file.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame containing the loaded data
        
    Raises:
        FileNotFoundError: If the specified file does not exist
        ValueError: If the file is not a valid CSV
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Error reading CSV file '{filepath}': {str(e)}")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic cleaning operations on a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    return df


def save_data(df: pd.DataFrame, filepath: str, format: str = 'csv') -> None:
    """
    Save DataFrame to file.
    
    Args:
        df: DataFrame to save
        filepath: Output file path
        format: Output format ('csv', 'json', 'parquet')
    """
    if format == 'csv':
        df.to_csv(filepath, index=False)
    elif format == 'json':
        df.to_json(filepath, orient='records', indent=2)
    elif format == 'parquet':
        df.to_parquet(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get a summary of the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary containing summary statistics
    """
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'missing_values': df.isnull().sum().to_dict(),
        'dtypes': df.dtypes.astype(str).to_dict()
    }
