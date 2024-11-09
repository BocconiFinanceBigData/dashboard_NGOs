import pandas as pd
import numpy as np
from wordcloud import WordCloud
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import io
import base64


def analyze_campaign_sentiment(df):
    sentiment_counts = df['sentiment'].value_counts().sort_index()
    sentiment_map = {
        -2: 'Very Negative', -1: 'Negative',
        0: 'Neutral', 1: 'Positive', 2: 'Very Positive'
    }

    return pd.DataFrame({
        'Sentiment': [sentiment_map[i] for i in sentiment_counts.index],
        'Count': sentiment_counts.values,
        'Percentage': (sentiment_counts.values / len(df) * 100).round(2)
    })


def analyze_prominence_distribution(df):
    prominence_counts = df[df['prominence'] != 0]['prominence'].value_counts().sort_index()
    prominence_map = {
        1: 'Mentioned in document',
        2: 'Mentioned in text',
        3: 'First paragraph',
        4: 'Headline'
    }

    return pd.DataFrame({
        'Level': [prominence_map[i] for i in prominence_counts.index],
        'Count': prominence_counts.values,
        'Percentage': (prominence_counts.values / len(df) * 100).round(2)
    })




def analyze_company_distribution(df):
    """Analyze most targeted companies"""
    company_counts = df['company_parent'].value_counts().reset_index()
    company_counts.columns = ['Company', 'Count']
    return company_counts


def analyze_top_companies(df, top_n=20):
    """Analyze most targeted companies with industry sector"""
    # Include industry sector in the analysis
    company_stats = df.groupby(['company_parent', 'corp_industry_sector1']).agg({
        'uid_archive': 'count',
        'sentiment': 'mean',
        'prominence': 'mean'
    }).round(2)

    company_stats = company_stats.reset_index()
    company_stats.columns = ['company_parent', 'industry_sector', 'campaign_count', 'avg_sentiment', 'avg_prominence']
    company_stats = company_stats.sort_values('campaign_count', ascending=False)

    return company_stats.head(top_n)


def analyze_country_network(df):
    """Analyze country relationships and create activity map"""
    country_pairs = []

    # Collect country pairs
    for _, row in df.iterrows():
        active_countries = set()
        target_countries = set()

        # Collect active countries
        for i in range(1, 7):
            if pd.notna(row[f'active_country{i}']):
                active_countries.add(row[f'active_country{i}'])

        # Collect target countries
        for i in range(1, 7):
            if pd.notna(row[f'target_country{i}']):
                target_countries.add(row[f'target_country{i}'])

        # Create pairs
        for ac in active_countries:
            for tc in target_countries:
                country_pairs.append({
                    'source': ac,
                    'target': tc
                })

    # Convert to DataFrame and count frequencies
    country_df = pd.DataFrame(country_pairs)
    country_counts = country_df.groupby(['source', 'target']).size().reset_index(name='weight')

    # Calculate activity levels for choropleth
    countries = set(country_counts['source'].unique()) | set(country_counts['target'].unique())
    country_activity = []

    for country in countries:
        source_activity = country_counts[country_counts['source'] == country]['weight'].sum()
        target_activity = country_counts[country_counts['target'] == country]['weight'].sum()
        country_activity.append({
            'country': country,
            'activity': source_activity + target_activity
        })

    return pd.DataFrame(country_activity)


def analyze_ngo_distribution(df):
    """Analyze NGO participation excluding empty values and '0'"""
    ngo_counts = []

    # Process each NGO column
    for i in range(1, 6):
        ngo_col = f'ngo_name{i}'
        # Filter out empty, '0', 'nan', 'NaN', and None values
        valid_ngos = df[
            df[ngo_col].notna() &
            (df[ngo_col] != '0') &
            (df[ngo_col].str.lower() != 'nan') &
            (df[ngo_col] != '')
            ][ngo_col]

        if not valid_ngos.empty:
            counts = valid_ngos.value_counts()
            ngo_counts.extend([(ngo, count) for ngo, count in counts.items()])

    # Combine all counts
    ngo_df = pd.DataFrame(ngo_counts, columns=['NGO', 'Count'])
    ngo_df = ngo_df.groupby('NGO')['Count'].sum().reset_index()

    # Additional filter to remove any remaining unwanted values
    ngo_df = ngo_df[
        ~ngo_df['NGO'].isin(['0', 'nan', 'NaN', 'None']) &
        (ngo_df['NGO'].str.len() > 1)  # Remove single character entries
        ]

    return ngo_df.sort_values('Count', ascending=False)


def generate_wordcloud(df, dataset_name):
    """Generate wordcloud from issues and save as PNG"""

    def clean_text(text):
        if pd.isna(text) or text == '0' or text.lower() == 'nan':
            return ''
        return str(text).strip()

    # Combine and clean all issues
    all_issues = ' '.join([
        clean_text(issue) for issue in
        df['issue_name1'].astype(str) + ' ' +
        df['issue_name2'].astype(str) + ' ' +
        df['issue_name3'].astype(str)
    ])

    # Additional cleaning steps
    import re

    # Remove non-meaningful words and special characters
    words_to_remove = ['nan', 'none', '0', 'null', 'undefined']
    pattern = '|'.join(r'\b{}\b'.format(word) for word in words_to_remove)
    all_issues = re.sub(pattern, '', all_issues, flags=re.IGNORECASE)

    # Remove multiple spaces and strip
    all_issues = ' '.join(all_issues.split())

    # Generate word cloud with cleaned text
    wordcloud = WordCloud(
        width=1600,
        height=400,
        background_color='white',
        min_word_length=3,  # Ignore very short words
        collocations=True,  # Include common word pairs
        stopwords=set(words_to_remove)  # Additional stopwords
    ).generate(all_issues)

    # Ensure data directory exists
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)

    # Save the wordcloud image
    image_path = data_dir / f'wordcloud_{dataset_name}.png'
    wordcloud.to_file(str(image_path))

    return str(image_path)