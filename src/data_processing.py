import os
import pandas as pd
import pickle
from pathlib import Path

def load_processed_data():
    """Load preprocessed sigwatch_data for both datasets"""
    data_dir = Path('data')

    # Load combined dataset results
    with open(data_dir / 'processed_combined.pkl', 'rb') as f:
        combined_results = pickle.load(f)

    # Load finance dataset results
    with open(data_dir / 'processed_finance.pkl', 'rb') as f:
        finance_results = pickle.load(f)

    return combined_results, finance_results

def load_combined_data(folder_path='sigwatch_data/'):
    """Load and combine all .dta files"""
    data_frames = []
    for file in os.listdir(folder_path):
        if file.endswith('.dta'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_stata(file_path)
            data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)

def create_finance_df(combined_df):
    """Create finance sector subset"""
    finance_keywords = [
        'finance', 'bank', 'insurance', 'invest',
        'asset', 'capital', 'credit', 'financial',
        'fund', 'wealth', 'securities', 'trading'
    ]
    finance_mask = combined_df['corp_industry_sector1'].str.lower().str.contains(
        '|'.join(finance_keywords),
        na=False
    )
    return combined_df[finance_mask].copy()

def load_data():
    """Load both datasets"""
    combined_df = load_combined_data()
    finance_df = create_finance_df(combined_df)
    return combined_df, finance_df
