# PRESSURE DISPLAY SERVER FOR ISOLTRAP 

#  Python main file

#  Written by: 
# 	Lukas Nies <Lukas.Nies@cern.ch> 

# Version 1.0
# 30.11.2019

# Dependencies:
#	- Dash: https://plot.ly/dash/
#	- Plotly: https://plot.ly
#	- etc (find standard libraries in header)

# Installation:
# 	- Use pip to install all needed dependencies

# Run:
#	- Adjust absolute path of the pressure data
#	- Run .py file in your Python terminal
#	- Server is opened in the background, displays software in browser of your choice
#	- Adjust the HTML formatting if needed

import pandas as pd
import glob
import plotly
import plotly.graph_objects as go
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
from dash.dependencies import Input, Output, State

# pip install pyorbital
from pyorbital.orbital import Orbital
satellite = Orbital('TERRA')

external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']

colors = {
    'background': '#111111',
    'plot_background': 'rgb(51, 54, 65)',
    'text': '#7FDBFF',
    'text2': 'rgb(50, 67, 118)',
}

pathtodata = "/home/lukas/Programs/GitHub/Pressure_Display/data/*dat"
pathtoisoltrap = "/home/lukas/Programs/GitHub/Pressure_Display/logos/ISOLTRAP_logo.png"
pathtocern = "/home/lukas/Programs/GitHub/Pressure_Display/logos/Logo-Outline-web-Blue@200.png"
encoded_isoltrap = base64.b64encode(open(pathtoisoltrap, 'rb').read())
encoded_cern = base64.b64encode(open(pathtocern, 'rb').read())

cnames = ['VI','Datetime', 'Time', 'Alkali', 'Alkali_status', 'ISOLDE/Buncher', 'ISOLDE/Buncher_status',
          'Buncher/Isep1', 'Buncher/Isep1_status', 'Buncher/Isep2', 'Buncher/Isep2_status', 
          'MR-ToF_UHV', 'MR-ToF_UHV_status', 'Isep/Cube', 'Isep/Cube_status', 'Cube', 'Cube_status', 'Lower_Diff', 'Lower_Diff_status', 
          'Upper_Diff', 'Upper_Diff_status', 'Cryopot', 'Cryopot_status', 'Cryopump', 'Cryopump_status', 
          'MCP5', 'MCP5_status', 'Rough0', 'Rough0_status', 'Rough1', 'Rough1_status',
          'IsepPrevac2', 'IsepPrevac2_status', 'IsepPrevac1', 'IsepPrevac1_status', 
          'Rough2', 'Rough2_status', 'Rough3', 'Rough3_status', 'Rough4', 'Rough4_status',
          'Rough5', 'Rough5_status', 'Rough6', 'Rough6_status', 'Helium', 'Helium_status',
          'LIS', 'LIS_status'
         ]
uhv_pumps = ['Alkali', 'ISOLDE/Buncher', 'Buncher/Isep1', 'Buncher/Isep2', 
             'MR-ToF_UHV', 'Isep/Cube', 'Cube', 'Lower_Diff', 'Upper_Diff', 'Cryopot', 'Cryopump',
              'MCP5', 'Helium', 'LIS'
            ]
pre_pumps = ['Rough0', 'Rough1', 'IsepPrevac2', 'IsepPrevac1', 'Rough2', 'Rough3', 'Rough4',
             'Rough5', 'Rough6'
            ]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
        html.H1(
            children='ISOLTRAP Live Pressure Monitor',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'font-size': '50px',
                'font-weight': 'bold',
                'top' : -60,
            }
        ),
        html.Img(src='data:image/png;base64,{}'.format(encoded_isoltrap),
                style={
                    'height' : '10%',
                    'width' : '10%',
                    'position' : 'relative',
                    # 'float' : 'right',
                    'padding-top' : 0,
                    'padding-right' : 0,
                    'top' : -60,
                    'left' : +280,
                },
        ),
        html.Img(src='data:image/png;base64,{}'.format(encoded_cern),
                style={
                    'height' : '5%',
                    'width' : '5%',
                    'position' : 'relative',
                    # 'float' : 'right',
                    'padding-top' : 0,
                    'padding-right' : 0,
                    'top' : -60,
                    'right' : -1100,
                },
        ),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )
    ])
])
@app.callback(Output('live-update-graph', 'figure'), 
    [Input('interval-component', 'n_intervals')], [State('live-update-graph', 'figure')])
def update_graph_live(n, existing):
    df = load_data(path=pathtodata, n_files=10)
    # Create the graph with subplots
    fig = plotly.subplots.make_subplots(rows=2, cols=1, vertical_spacing=0.05)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 10, 't': 70
    }
    for pump in uhv_pumps:
        fig.append_trace(go.Scattergl(
            x=df['Datetime'],
            y=df[pump],
            mode="lines",
            name=pump,
            legendgroup="UHV",
            line=dict(width=3),
        ), 1, 1)
    for pump in pre_pumps:
        fig.append_trace(go.Scattergl(
            x=df['Datetime'],
            y=df[pump],
            mode="lines",
            name=pump,
            legendgroup="PRE",
            line=dict(width=3),
        ), 2, 1)
    fig['layout']['yaxis1'].update(title='Pressure [mbar]', type='log')
    fig['layout']['yaxis2'].update(title='Pressure [mbar]', type='log')
    fig.update_layout(
        legend=go.layout.Legend(
            x=+0.5,
            xanchor="center",
            y=1.15,
            yanchor="top",
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=16,
                color=colors['text']
            ),
            bgcolor=colors['plot_background'],
            bordercolor=colors['text'],
            borderwidth=2,
            orientation="h"
        )
    )
    fig.update_layout(
        height=750, width=1600,
        plot_bgcolor= colors['plot_background'],
        paper_bgcolor= colors['background'],
        font = {
            'color': colors['text'],
            'size': 18
        },
        xaxis1 = {
            'gridcolor' : 'rgb(159, 197, 232)',
        },
        yaxis1 = {
            'gridcolor' : 'rgb(159, 197, 232)',
            'exponentformat' : 'E',
            'showexponent' : 'all',
        },
        yaxis2 = {
            'gridcolor' : 'rgb(159, 197, 232)',
            'exponentformat' : 'E',
            'showexponent' : 'all',
        },
    )


    return fig

def load_data(path, n_files):
    data_list = glob.glob(path)
    data_list.sort(key = lambda x: x.split("/")[-1])
    # Only take the latest n_files for the data
    data_list = data_list[-n_files:]
    
    if (len(data_list) < 1):
        return 0
    i = 0
    for filename in data_list:
        if i == 0:
            master_df = pd.read_csv(filename, header=1, sep="\t", error_bad_lines=False, names=cnames)
        else:
            df = pd.read_csv(filename, header=1, sep="\t", error_bad_lines=False, names=cnames)
            master_df = master_df.append(df, ignore_index = True)
        i += 1
    master_df = master_df.drop(['VI'], axis=1)
    # Convert the time into a convertable format
    for index, row in master_df.iterrows():
        date = master_df.iloc[index].Datetime
        substr1 = master_df.iloc[index].Time.split(':')[0]
        substr2 = master_df.iloc[index].Time.split(':')[1]
        substr3 = master_df.iloc[index].Time.split(':')[2]
        intsubstr1 = int(substr1)
        intsubstr2 = int(substr2)
        # if (intsubstr1 + 12 >= 24):
        #     intsubstr1 = intsubstr1 - 12
        # else:
        #     intsubstr1 = intsubstr1 + 12
        if (str(master_df.iloc[index].Time[-2:]) == "AM"):
            if (intsubstr1 == 12):
                intsubstr1 = intsubstr1 - 12
            master_df.at[index, 'Time'] = date+" "+str(intsubstr1)+":"+substr2+":"+str(substr3[:2])
        else:
            if (intsubstr1 < 12):
                intsubstr1 = intsubstr1 + 12
            master_df.at[index, 'Time'] = date+" "+str(intsubstr1)+":"+substr2+":"+str(substr3[:2])
        # Convert time to datetime
        master_df.at[index, 'Datetime'] = datetime.datetime.strptime(master_df.iloc[index].Time, '%m/%d/%Y %H:%M:%S')
    return master_df 

if __name__ == '__main__':
    app.run_server(debug=True)
