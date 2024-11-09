import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

from src.data_processing import load_data
from src.analysis import (
    analyze_campaign_sentiment,
    analyze_prominence_distribution,
    analyze_top_companies,
    generate_wordcloud
)

# Load sigwatch_data
df_combined, df_finance = load_data()

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Needed for deployment

# Create layout
app.layout = html.Div([
    dbc.Container([
        # Header and Dataset Selection
        html.H1("NGO Campaign Analysis Dashboard", className="text-center my-4"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='dataset-selector',
                    options=[
                        {'label': 'All Companies', 'value': 'combined'},
                        {'label': 'Financial Sector', 'value': 'finance'}
                    ],
                    value='combined',
                    className="mb-4"
                )
            ], width=6)
        ], justify="center"),

        # Visualizations
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Campaign Sentiment"),
                    dbc.CardBody([dcc.Graph(id='sentiment-pie')])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Campaign Prominence"),
                    dbc.CardBody([dcc.Graph(id='prominence-bar')])
                ])
            ], width=6)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Company Analysis"),
                    dbc.CardBody([dcc.Graph(id='company-scatter')])
                ])
            ], width=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Campaign Issues"),
                    dbc.CardBody([html.Img(id='wordcloud-img', className="img-fluid")])
                ])
            ], width=12)
        ])
    ], fluid=True)
])


# Callbacks
@app.callback(
    [Output('sentiment-pie', 'figure'),
     Output('prominence-bar', 'figure'),
     Output('company-scatter', 'figure'),
     Output('wordcloud-img', 'src')],
    [Input('dataset-selector', 'value')]
)
def update_dashboard(selected_dataset):
    # Select dataset
    df = df_combined if selected_dataset == 'combined' else df_finance

    # Generate analyses
    sentiment_df = analyze_campaign_sentiment(df)
    prominence_df = analyze_prominence_distribution(df)
    companies_df = analyze_top_companies(df)
    wordcloud = generate_wordcloud(df)

    # Create figures
    sentiment_fig = px.pie(
        sentiment_df,
        values='Count',
        names='Sentiment',
        title=f"Total Campaigns: {sentiment_df['Count'].sum():,}",
        hover_data=['Count']
    )

    prominence_fig = px.bar(
        prominence_df,
        x='Level',
        y='Count',
        color='Level',
        text='Count'
    )

    company_fig = px.scatter(
        companies_df.reset_index(),
        x='avg_sentiment',
        y='avg_prominence',
        size='campaign_count',
        hover_data=['company_parent'],
        labels={'avg_sentiment': 'Average Sentiment',
                'avg_prominence': 'Average Prominence',
                'company_parent': 'Company'}
    )

    return sentiment_fig, prominence_fig, company_fig, f"data:image/png;base64,{wordcloud}"


if __name__ == '__main__':
    app.run_server(debug=True)