import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.data_processing import load_processed_data
from pathlib import Path
# Page config
st.set_page_config(
    page_title="NGO Campaign Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load preprocessed sigwatch_data
@st.cache_data
def load_cached_data():
    return load_processed_data()

try:
    combined_results, finance_results = load_cached_data()
    st.success("Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading sigwatch_data: {str(e)}")
    st.stop()

# Title and dataset selector
st.title("NGO Campaign Analysis Dashboard")
selected_dataset = st.selectbox(
    "Select Dataset",
    options=['combined', 'finance'],
    format_func=lambda x: "All Companies" if x == 'combined' else "Financial Sector"
)

# Select dataset results
results = combined_results if selected_dataset == 'combined' else finance_results

# Use preprocessed results directly
sentiment_df = results['sentiment']
prominence_df = results['prominence']
ngo_df = results['ngo_distribution']
company_df = results['company_distribution']
companies_analysis = results['companies_analysis']
country_activity = results['country_activity']
wordcloud = results['wordcloud']

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Campaign Sentiment")
    fig_sentiment = px.pie(
        sentiment_df,
        values='Count',
        names='Sentiment',
        title=f"Total Campaigns: {sentiment_df['Count'].sum():,}",
        hole=0.3,
        hover_data=['Count']
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col2:
    st.subheader("Campaign Prominence")
    fig_prominence = px.pie(
        prominence_df,
        names='Level',
        values='Count',
        color='Level',
        hole=0.3,
        hover_data=['Count']
    )
    st.plotly_chart(fig_prominence, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("NGO Participation")
    fig_ngo = px.pie(
        ngo_df.head(10),
        values='Count',
        names='NGO',
        title='Top 10 NGOs by Campaign Participation',
        hole=0.3,
        hover_data=['Count']
    )
    st.plotly_chart(fig_ngo, use_container_width=True)

with col4:
    st.subheader("Company Targeting")
    fig_company = px.pie(
        company_df.head(10),
        values='Count',
        names='Company',
        title='Top 10 Targeted Companies',
        hole=0.3,
        hover_data=['Count']
    )
    st.plotly_chart(fig_company, use_container_width=True)

# Company Analysis
st.subheader("Company Analysis")
fig_companies = px.scatter(
    companies_analysis.reset_index(),
    x='avg_sentiment',
    y='avg_prominence',
    size='campaign_count',
    color='industry_sector',
    hover_data=['company_parent'],
    labels={
        'avg_sentiment': 'Average Sentiment',
        'avg_prominence': 'Average Prominence',
        'company_parent': 'Company'
    }
)
st.plotly_chart(fig_companies, use_container_width=True)

# Global Campaign Activity
st.subheader("Global Campaign Activity")
fig_map = px.choropleth(
    country_activity,
    locations='country',
    locationmode='country names',
    color='activity',
    hover_name='country',
    color_continuous_scale='Viridis',
    title='Campaign Activity Intensity by Country'
)
fig_map.update_layout(height=600)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Campaign Issues")

data_dir = Path('data')
wordcloud_paths = {
    'combined': data_dir / 'wordcloud_combined.png',
    'finance': data_dir / 'wordcloud_finance.png'
}
# Check if the file exists before trying to display it
wordcloud_path = wordcloud_paths[selected_dataset]
if wordcloud_path.exists():
    st.image(
        str(wordcloud_path),
        use_column_width=True,
        caption=f"Word Cloud of Campaign Issues - {'All Companies' if selected_dataset == 'combined' else 'Financial Sector'}"
    )
else:
    st.error(f"Word cloud image not found at {wordcloud_path}")
    st.write("Please ensure the preprocessing script has been run and generated the word cloud images.")