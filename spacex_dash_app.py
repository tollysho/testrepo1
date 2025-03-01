# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                # Task 1: Add a dropdown list to enable Launch Site selection
            dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                ],
            value='ALL',  # Default value for the dropdown
            placeholder="Select a Launch Site here",
            searchable=True,
            style={'width': '50%', 
                    'padding': '3px', 
                    'font-size': 20, 
                    'text-align': 'center'}
),

                               
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                # Add a slider for selecting payload range (Task 3)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, 
                                                max=10000, 
                                                step=1000, 
                                                marks={0: '0',
                                                    1000: '1000',
                                                    2000: '2000',
                                                    3000: '3000',
                                                    4000: '4000',
                                                    5000: '5000',
                                                    6000: '6000',
                                                    7000: '7000',
                                                    8000: '8000',
                                                    9000: '9000',
                                                    10000: '10000'},
                                                    value=[min_payload, max_payload]  # Set default value to the range of the dataset
),



                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ]),

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If the selected site is 'ALL', we need to calculate total success vs failure across all sites
    if entered_site == 'ALL':
        # Count the number of successes (class=1) and failures (class=0) for all data
        success_count = spacex_df[spacex_df['class'] == 1].shape[0]
        failure_count = spacex_df[spacex_df['class'] == 0].shape[0]
        
        # Create a DataFrame for plotting
        data = pd.DataFrame({
            'Success/Failure': ['Success', 'Failure'],
            'Count': [success_count, failure_count]
        })
        
        # Create a pie chart for all sites showing Success vs Failure
        fig = px.pie(data, values='Count', names='Success/Failure', title='Launch Success vs Failure for All Sites')
    
    else:
        # If a specific site is selected, filter the data for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count the success (class=1) and failure (class=0) for the selected site
        data = filtered_df['class'].value_counts().reset_index()
        data.columns = ['Success/Failure', 'Count']
        
        # Create a pie chart for the selected site showing Success vs Failure
        fig = px.pie(data, values='Count', names='Success/Failure', title=f'Success vs Failure for {entered_site}')
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(entered_site, payload_range):
    # Filter the data based on the selected site
    filtered_df = spacex_df
    
    if entered_site != 'ALL':
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    
    # Filter the data based on the selected payload range
    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) & 
                              (filtered_df['Payload Mass (kg)'] <= max_payload)]
    
    # Create a scatter plot of Payload Mass vs. Launch Success
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category',  # Color by booster version
        title=f'Success vs Payload Mass for {entered_site}' if entered_site != 'ALL' else 'Success vs Payload Mass for All Sites',
        labels={'class': 'Launch Success'},
        color_discrete_map={'FT': 'green', 'Block 5': 'blue', 'Block 3': 'purple'}  # Customize color for boosters
    )
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
