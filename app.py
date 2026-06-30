import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# -----------------------------------
# Load CSV
# -----------------------------------
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# -----------------------------------
# Initialize app
# -----------------------------------
app = dash.Dash(__name__)

# -----------------------------------
# Layout
# -----------------------------------
app.layout = html.Div(children=[

    html.H1(
        "SpaceX Launch Records Dashboard",
        style={'textAlign': 'center'}
    ),

    # Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site}
            for site in spacex_df['Launch Site'].unique()
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),

    # Pie chart
    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    html.P("Payload Range (Kg):"),

    # Range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter plot
    dcc.Graph(id='success-payload-scatter-chart')

])

# -----------------------------------
# Pie chart callback
# -----------------------------------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):

    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == selected_site
        ]

        success_count = filtered_df['class'].value_counts().reset_index()
        success_count.columns = ['Outcome', 'Count']

        fig = px.pie(
            success_count,
            names='Outcome',
            values='Count',
            title=f'Success vs Failure for {selected_site}'
        )

    return fig


# -----------------------------------
# Scatter plot callback
# -----------------------------------
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):

    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs Launch Outcome for All Sites'
        )
    else:
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == selected_site
        ]

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs Launch Outcome for {selected_site}'
        )

    return fig


# -----------------------------------
# Run app
# -----------------------------------

if __name__ == '__main__':
    app.run(debug=True)