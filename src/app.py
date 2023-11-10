import pandas as pd
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import requests
from dash.dependencies import Input, Output, State

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

url = "https://covid-193.p.rapidapi.com/statistics"

headers = {
    "X-RapidAPI-Key": "d4215e215dmsh48620532d36a5f9p1d2107jsn621bacd06f8a",
    "X-RapidAPI-Host": "covid-193.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
df = pd.DataFrame(response.json()['response'])

covid_19_clean_complete = pd.read_csv('covid_19_clean_complete.csv')
country_df = covid_19_clean_complete.copy()

cases = pd.DataFrame()
for i in df['cases']:
    cases = pd.concat([cases, pd.DataFrame([i])], ignore_index=True)
cases = cases.drop(columns=['new', '1M_pop']).rename(columns={'total': 'total_cases'})

tests = pd.DataFrame()
for i in df['tests']:
    tests = pd.concat([tests, pd.DataFrame([i])], ignore_index=True)
tests = tests[['total']].rename(columns={'total': 'total_tests'})

deaths = pd.DataFrame()
for i in df['deaths']:
    deaths = pd.concat([deaths, pd.DataFrame([i])], ignore_index=True)
deaths = deaths.drop(columns=['new', '1M_pop']).rename(columns={'total': 'deaths'})

df = df.drop(columns=['day', 'cases', 'deaths', 'tests'])
df = pd.concat([df, deaths, cases, tests], axis=1)

df['time'] = pd.to_datetime(df['time'])
df['population'] = pd.to_numeric(df['population'], errors='coerce').fillna(0).astype('int')
df['total_tests'] = pd.to_numeric(df['total_tests'], errors='coerce').fillna(0).astype('int')
df['active'] = pd.to_numeric(df['active'], errors='coerce').fillna(0).astype('int')
df['critical'] = pd.to_numeric(df['critical'], errors='coerce').fillna(0).astype('int')
df['recovered'] = pd.to_numeric(df['recovered'], errors='coerce').fillna(0).astype('int')
df['total_cases'] = pd.to_numeric(df['total_cases'], errors='coerce').fillna(0).astype('int')
df['deaths'] = pd.to_numeric(df['deaths'], errors='coerce').fillna(0).astype('int')

continent = df['continent'].value_counts().reset_index()
total_tests = 0
for i in continent['continent']:
    temp_df = df[df['continent'] == i].iloc[:-1]
    total_tests = total_tests + temp_df['total_tests'].sum()
total_cases = df[df['continent'] == "All"]["total_cases"]
total_recovered = df[df['continent'] == "All"]["recovered"]
total_deaths = df[df['continent'] == "All"]["deaths"]

options = [
    {'label': 'All', 'value': 'All'},
    {'label': 'Africa', 'value': 'Africa'},
    {'label': 'Asia', 'value': 'Asia'},
    {'label': 'Europe', 'value': 'Europe'},
    {'label': 'North-America', 'value': 'North-America'},
    {'label': 'South-America', 'value': 'South-America'},
    {'label': 'Oceania', 'value': 'Oceania'}
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H2(children="Covid-19 Statistics Across Globe", style={'color': '#fff', 'text-align': 'center'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Tests", style={'text-align': 'center'}),
                    html.H4(total_tests, style={'text-align': 'center'})
                ], className='card-body')
            ], className='card bg-info')
        ], className='col-md-3'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Cases", style={'text-align': 'center'}),
                    html.H4(total_cases, style={'text-align': 'center'})
                ], className='card-body')
            ], className='card bg-warning')
        ], className='col-md-3'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Deaths", style={'text-align': 'center'}),
                    html.H4(total_deaths, style={'text-align': 'center'})
                ], className='card-body')
            ], className='card bg-danger')
        ], className='col-md-3'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Recovered", style={'text-align': 'center'}),
                    html.H4(total_recovered, style={'text-align': 'center'})
                ], className='card-body')
            ], className='card bg-success')
        ], className='col-md-3')
    ], className='row'),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H2(children="Covid-19 Continent Wise Data", style={'text-align': 'center'}),
                    html.H3(children="Total Cases", style={'text-align': 'center'}),
                    dcc.Dropdown(id="picker", options=options, value="All"),
                    dcc.Graph(id='bar')
                ], className='card-body')
            ], className='card')
        ], className='col-md-10'),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(children="Total Tests", style={'text-align': 'center'}),
                        html.H4(id='uni1', style={'text-align': 'center'})
                    ], className='card-body')
                ], style={'width': '100%', 'height': '190px'}, className='card bg-info')
            ], className='row'),
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(children="Total Cases", style={'text-align': 'center'}),
                        html.H4(id='uni2', style={'text-align': 'center'})
                    ], className='card-body')
                ], style={'width': '100%', 'height': '190px'}, className='card bg-warning')
            ], className='row'),
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(children="Total Deaths", style={'text-align': 'center'}),
                        html.H4(id='uni3', style={'text-align': 'center'})
                    ], className='card-body')
                ], style={'width': '100%', 'height': '190px'}, className='card bg-success')
            ], className='row')
        ], className='col-md-2')
    ], className='row'),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(id="sub-picker", options=[], multi=False)
                ], className='card-body')
            ], className='card')
        ], className='col-md-12')
    ], className='row'),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(id='line1')
                ], className='card-body')
            ], className='card')
        ], className='col-md-10'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3(children='% death rate per country', style={'text-align': 'center'}),
                    html.H4(id='uni4', style={'text-align': 'center'})
                ], className='card-body')
            ], style={'width': '100%', 'height': '80px'}, className='card bg-danger')
        ], className='col-md-2'),
    ], className='row')
], className='container')


@app.callback(Output('bar', 'figure'), [Input('picker', 'value')])
def update_graph(val):
    df1 = df[df['continent'] == val].iloc[:-1]
    return {'data': [go.Bar(x=df1['country'],
                            y=df1['total_cases'])],
            'layout': go.Layout(xaxis={'title': "Country's name"},
                                yaxis={'title': 'Total Cases'})}


@app.callback(Output('uni1', 'children'), [Input('picker', 'value')], [State('picker', 'value')])
def continent_value_1(val1, selected_value):
    df1 = df[df['continent'] == val1].iloc[:-1]
    return df1['total_tests'].sum()


@app.callback(Output('uni2', 'children'), [Input('picker', 'value')], [State('picker', 'value')])
def continent_value_2(val2, selected_value):
    df1 = df[df['continent'] == val2]
    return df1['total_cases'].iloc[-1]


@app.callback(Output('uni3', 'children'), [Input('picker', 'value')], [State('picker', 'value')])
def continent_value_3(val3, selected_value):
    df1 = df[df['continent'] == val3]
    return df1['deaths'].iloc[-1]


@app.callback(Output('sub-picker', 'options'), [Input('picker', 'value')], [State('picker', 'value')])
def update_sub_picker_options(selected_continent, current_value):
    if selected_continent == 'All':
        return [{'label': country, 'value': country} for country in df['country'].unique()[:-4]]
    else:
        return [{'label': country, 'value': country} for country in
                df[df['continent'] == selected_continent]['country'].unique()[-6:-1]]


@app.callback(Output('line1', 'figure'), [Input('sub-picker', 'value')], [State('sub-picker', 'value')])
def country_details(select1, current):
    df1 = country_df[country_df['Country/Region'] == select1]
    return {'data': [go.Scatter(x=df1['Date'], y=df1['Confirmed'], mode='lines', name='Confirmed Cases')],
            'layout': go.Layout(title="line-plot",
                                xaxis={'title': 'Date', 'type': 'date'},
                                yaxis={'title': 'No. of Cases'})}


@app.callback(Output('uni4', 'children'), [Input('sub-picker', 'value')], [State('sub-picker', 'value')])
def country_details1(select1, current):
    df1 = country_df[country_df['Country/Region'] == select1]
    return round(df1['Deaths'].sum()/df1['Confirmed'].sum()*100,2)


if __name__ == "__main__":
    app.run_server(debug=True)
