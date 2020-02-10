import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import seaborn as sns
import dash_table
from dash.dependencies import Input, Output, State
import mysql.connector

conn = mysql.connector.connect(host='localhost',user='root',passwd='abcd1234',use_pure = True)
cursor = conn.cursor(dictionary = True)
cursor.execute('USE ujian2')

def generate_table(dataframe, page_size=10):
    return dash_table.DataTable(
        id='dataTable',
        columns=[{
        "name": i,
        'id': i
        } for i in dataframe['Claim Site'].unique()],
        data=dataframe.to_dict('records'),
        page_action='native',
        page_current=0,
        page_size=page_size
    )

cursor.execute('SELECT * from ujian2.tsa_claims_dashboard_ujian')
result = cursor.fetchall()
tsa = pd.DataFrame(result)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1("Ujian Modul 2 Dashboard TSA"),
    html.Div(children="""
        Created by: Nicholas Candra 
        """),
        dcc.Tabs(children = [
            dcc.Tab(value= 'Tab1', label= 'Data Frame Table', children= [
            html.Div([html.H1("DATAFRAME TSA")]),
            html.Div([
                    html.P('Claim Site'),
                    dcc.Dropdown(value='',
                    id='table-claim',
                    options=[{'label':'All','value':''},
                    {'label':'Checked Baggage','value':'Checked Baggage'},
                    {'label':'Checkpoint','value':'Checkpoint'},
                    {'label':'Other','value':'Other'}])
                ]),
            html.Div([html.P('Max Rows:'),
            # dcc.Input(id='input-row', type='number', value=10)
            dcc.Input(id='input-row', value=10)]),
            html.Div([html.Button('search', id='maxrow')]),
            html.Div(id='div-table', children=[generate_table(tsa,page_size=10)])
            ]),
            dcc.Tab(value= 'Tab2', label= 'Bar-Chart', children= [
            html.Div(children=[
                html.Div([
                    html.P('Y1: '),
                    dcc.Dropdown(value='Claim Amount',
                    id='filter-y1',
                    options=[{'label':'Claim Amount','value':'Claim Amount'},
                    {'label':'Close Amount','value':'Close Amount'},
                    {'label':'Day Differences','value':'Day Differences'},
                    {'label':'Amount Differences','value':'Amount Differences'}
                    ])
                ],className='col-3'),
                html.Div([
                    html.P('Y2: '),
                    dcc.Dropdown(value='Claim Amount',
                    id='filter-y2',
                    options=[{'label':'Claim Amount','value':'Claim Amount'},
                    {'label':'Close Amount','value':'Close Amount'},
                    {'label':'Day Differences','value':'Day Differences'},
                    {'label':'Amount Differences','value':'Amount Differences'}
                    ])
                ],className='col-3'),
                html.Div([
                html.P('X: '),
                dcc.Dropdown(value='Claim Type',
                id='filter-x',
                options=[{'label':'Claim Type','value':'Claim Type'},
                {'label':'Claim Site','value':'Claim Site'},
                {'label':'Disposition','value':'Disposition'}
                ])
                ],className='col-3')
            ],className='row'),
            dcc.Graph(
                id='graph-bar',
                figure={'data': [ 
                    {'x': tsa['Claim Type'], 'y': tsa['Claim Amount'], 'type':'bar', 'name':'Claim Amount'},
                    {'x': tsa['Claim Type'], 'y': tsa['Claim Amount'], 'type':'bar', 'name':'Claim Amount'}
                    ]})
        ],className='col-4'),
        dcc.Tab(value= 'Tab3', label= "Scatter-Chart", children= [
            dcc.Graph(
                id='graph-scatter',
                figure={'data':[
                    go.Scatter(
                        x=tsa[tsa['Claim Type']==i]['Claim Amount'],
                        y=tsa[tsa['Claim Type']==i]['Close Amount'],
                        mode='markers',
                        name='{}'.format(i)
                    ) for i in tsa['Claim Type'].unique()
                ],
                'layout':go.Layout(
                    xaxis={'title': 'Close Amount'},
                    yaxis={'title': 'Claim Amount'},
                    hovermode='closest'
                )}
            )
        ]),
        dcc.Tab(value= 'Tab4', label= "Pie-Chart", children= [
            html.Div([
                    html.P(''),
                    dcc.Dropdown(value='Claim Amount',
                    id='pie',
                    options=[{'label':'Claim Amount','value':'Claim Amount'},
                    {'label':'Close Amount','value':'Close Amount'},
                    {'label':'Day Differences','value':'Day Differences'},
                    {'label':'Amount Differences','value':'Amount Differences'}
                    ])]),
            dcc.Graph(
            id='graph-pie',
            figure={'data':[
                go.Pie(
                    labels = [i for i in tsa['Claim Type'].unique()],
                    values = [tsa[tsa['Claim Type']==i]['Claim Amount'].mean() for i in tsa['Claim Type'].unique()]
                )
            ],
            'layout':go.Layout(
                title='Mean Pie Chart'
            )}
        )
        ],className='col-4')
        ],
    content_style={
        'font_family':'Arial',
        'borderBottom':'1px solid #d6d6d6',
        'borderLeft':'1px solid #d6d6d6',
        'borderRight':'1px solid #d6d6d6',
        'padding':'44px'
    })
],
style={
    'maxWidth':'1200px',
    'margin': '0 auto'
})

@app.callback(
    Output(component_id = 'div-table', component_property = 'children'),
    [Input(component_id = 'maxrow', component_property = 'n_clicks')],
    [State(component_id = 'table-claim', component_property= 'value'),
    State(component_id = 'input-row', component_property = 'value')],
    Output(component_id = 'graph-bar', component_property = 'children'),
    [State(component_id = 'filter-y1', component_property = 'values'),
    State(component_id = 'filter-y2', component_property = 'values'),
    State(component_id = 'filter-x', component_property = 'values'),],
    Output(component_id = 'graph-pie', component_property = 'children'),
    State(component_id = 'pie', component_property = 'values')
)


def input_table(n_clicks, tclaim, row):
    cursor.execute('SELECT * from ujian2.tsa_claims_dashboard_ujian')
    result = cursor.fetchall()
    tsa = pd.DataFrame(result)
    if tclaim == 'Checked Baggage':
        tsa = tsa[tsa['Claim Site'] == 'Checked Baggage']
    if tclaim == 'Checkpoint':
        tsa = tsa[tsa['Claim Site'] == 'Checkpoint']
    if tclaim == 'Other':
        tsa = tsa[tsa['Claim Site'] == 'Other']
    children = [generate_table(tsa, page_size = row)]
    return children

if __name__ == '__main__':
    app.run_server(debug=True)