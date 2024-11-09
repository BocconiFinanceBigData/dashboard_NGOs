import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from analysis import (
    analyze_campaign_sentiment,
    analyze_prominence_distribution,
    analyze_ngo_distribution,
    analyze_company_distribution,
    analyze_top_companies,
    analyze_country_network,
    generate_wordcloud
)
from data_processing import load_data


def preprocess_and_save_data():
    """Preprocess data and save analysis results"""
    # Create data directory if it doesn't exist
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    # Load raw data
    print("Loading raw data...")
    df_combined, df_finance = load_data()

    # Process both datasets
    datasets = {
        'combined': df_combined,
        'finance': df_finance
    }

    for dataset_name, df in datasets.items():
        print(f"\nProcessing {dataset_name} dataset...")

        # Generate wordcloud and save as PNG
        wordcloud_path = generate_wordcloud(df, dataset_name)

        # Perform all other analyses
        results = {
            'sentiment': analyze_campaign_sentiment(df),
            'prominence': analyze_prominence_distribution(df),
            'ngo_distribution': analyze_ngo_distribution(df),
            'company_distribution': analyze_company_distribution(df),
            'companies_analysis': analyze_top_companies(df),
            'country_activity': analyze_country_network(df),
            'wordcloud_path': wordcloud_path  # Store the path instead of the image data
        }

        # Save results
        output_file = data_dir / f'processed_{dataset_name}.pkl'
        with open(output_file, 'wb') as f:
            pickle.dump(results, f)

        print(f"Saved processed data to {output_file}")
        print(f"Saved wordcloud to {wordcloud_path}")


if __name__ == "__main__":
    preprocess_and_save_data()