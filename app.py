#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import math
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_daq as daq

import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
import json
import time
import numpy as np

from datetime import datetime, timedelta

MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoia2hneXRkMTIzIiwiYSI6ImNrbjFzcmFlaDA5OXgycG1ubDBoc2Q0MGsifQ.2AYcjBwvTBqLVoIbMnG3jw"
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

external_scripts = [
    'https://code.jquery.com/jquery-3.3.1.min.js'
]

app = dash.Dash(__name__,external_stylesheets = [dbc.themes.BOOTSTRAP],external_scripts=external_scripts)

world_path = 'custom.geo.json'
with open(world_path) as f:
    map_json = json.load(f)

# Dataset Processing
df = pd.read_csv('Final_mas_bom.csv')
df['date'] = pd.to_datetime(df['date'])
df = df[df['iso_code'].isin(['IRL','AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT','ROU','SVK','SVN','ESP','SWE'])]


#Date setup
sdate = datetime(2020, 3, 1)   # start date
edate = datetime(2021, 3, 2)   # end date

delta = edate - sdate       # as timedelta

days=[]
for i in range(delta.days + 1):
    day = sdate + timedelta(days=i)
    days.append(day)


#country_time_df = df.rename(columns={'iso_code':'iso_a3'})
#country_time_df['date'] = pd.to_datetime(country_time_df['date'])

def getCountryDf(country):
    #print(country)
    return df[df['country_region'] == country]

def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(pd.to_datetime(unix,unit='s').date())

def getMarks(start, end, Nth=50):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(days):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result

country_options = [{"label":country,'value':country} for country in df['country_region'].unique()]


indicators_map = {
'retail_and_recreation_percent_change_from_baseline': 'Retail and Recreation',
'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery and Pharmacy',
'parks_percent_change_from_baseline':'Parks',
'transit_stations_percent_change_from_baseline':'Transit Station',
'workplaces_percent_change_from_baseline':'Workplaces',
'residential_percent_change_from_baseline':'Residential',
}

glossary=dcc.Markdown('''
GLOSSARY:
- ***EU***: European Union
- ***Analysis period***: All data in the present analysis refers to the period between the 25th February 2020 and the 2nd March 2021.
- ***Analysis area***: This analysis is focused in European Union countries.
- ***Baseline***: Represents a normal value for that day of the week. It is the median value from the 5 week period Jan 3-Feb 6, 2020.
- ***Grocery and Pharmacy***: Visits to grocery shops and pharmacies (considered essential trips and should have approximately the same social distancing rules).
- ***Parks***: Includes visits to public gardens, castles, national forests, campgrounds and observation decks. Parks typically means official national parks and not the general outdoors found in rural areas.
- ***Percent change from baseline***: Percent change in the number of total visitors compared to the baseline for Transit stations, Parks, Workplaces, Grocery and Pharmacy. For Residential indicator, it represents the percent change of the average duration (hours) spent in those places.
- ***Residential***: Shows the percent change of the average duration (hours) spent in places of residence.
- ***Transit stations***: Includes visits to subway stations, sea ports, taxi stands, highway rest stops and car rental agencies.
- ***Workplaces***: Includes visits to places of employment.
''',className="panel-lower glossary")

glossary_2=dcc.Markdown('''
On 31 December 2019, the WHO was informed of cases of pneumonia of unknown cause in Wuhan City, China. Seven days later a novel coronavirus was identified as the cause by Chinese authorities and on the 30th of January 2020, the coronavirus outbreak was declared a public health emergency of international concern, WHO's highest level of alarm.  On the 11th of March 2020, over 118 000 cases had been reported in 114 countries, and 4291 deaths had been recorded. This rapid increase in the number of cases outside China led the WHO to announce that the outbreak could be characterized as a pandemic!
''',className="panel-lower glossary")
indicadores_options = [
    {'label': 'Retail and Recreation', 'value': 'retail_and_recreation_percent_change_from_baseline'},
    {'label': 'Grocery and Pharmacy', 'value': 'grocery_and_pharmacy_percent_change_from_baseline'},
    {'label': 'Parks', 'value': 'parks_percent_change_from_baseline'},
    {'label': 'Transit Station', 'value': 'transit_stations_percent_change_from_baseline'},
    {'label': 'Workplaces', 'value': 'workplaces_percent_change_from_baseline'},
    {'label': 'Residential', 'value': 'residential_percent_change_from_baseline'}
    
]

deaths_cases_toggle = daq.ToggleSwitch(
    id="control-panel-toggle-line",
    value=True,
    label=["New cases", "New Deaths"],
    color="#ffe102",
    style={"color": "#black"},
)

#dropdown_list = [html.Img(height="20px", src=app.get_asset_url("flags/"+country_iso+".svg"))   for country_iso in df['iso_code'].unique()]
#dropdown_list = [dbc.DropdownMenuItem(country_iso, id=country_iso+"_drop")   for country_iso in df['iso_code'].unique()]

#dropdown_country = dbc.DropdownMenu(
#                label="Dropright", children=dropdown_list, direction="up",id='country_drop'
#            ),

dropdown_country_elem = dcc.Dropdown(
        id='country_drop',
        options=country_options,
        value='Portugal',
        clearable=False,
        multi=False
    )

#dropdown_country = dbc.Row([dbc.Col(html.Div(id="flag")),dbc.Col(dropdown_country_elem)])

dropdown_country = html.Div(className="in-row",children=[html.Div(id="flag"),html.Div(dropdown_country_elem,id="satellite-dropdown")])

indicators = dcc.RadioItems(
        id='indicators',
        options=indicadores_options,
        value='retail_and_recreation_percent_change_from_baseline'
    )

dropdown_2 = dcc.Dropdown(
        id='indicators_multiple',
        options=indicadores_options,
        value=['workplaces_percent_change_from_baseline'],
        multi=True
    )

num_cases_cum = html.Div(
    id="indicator_1",
    className="panel-lower",
    children=[
        html.P(
            id="new_cases_in",
            className="number-indicator",
            children=["0"]
        )
    
    ,"Total Cases"]
)
num_deaths_cum = html.Div(
    id="indicator_2",
    className="panel-lower",
    children=[
        html.P(
            id="new_deaths_in",
            className="number-indicator",
            children=["0"]
        )
    
    ,"Total Deaths"]
)
line_chart = html.Div(
    className="panel-lower line-chart-div",
    children=[
        html.Div(
            className="graph-header",
            children=[
                html.H1(
                    className="graph-title", children=["Deaths/New Cases per million"]
                )
            ],
        ),
        dcc.Graph(
            id="line_chart"#,
            #config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
)

slider_time = dcc.Slider(
        id='map_slider',
        min=unixTimeMillis(sdate),
        max=unixTimeMillis(edate),
        value=unixTimeMillis(sdate),
        marks=getMarks(sdate, edate),
)
slider_value = html.P(
            id="slider_label",
            className="date-indicator",
            children=["0"]
        )

slider_container= html.Div(id="slider-container",children=[slider_value,slider_time])

heatmap_section = html.Div(
    className="panel-lower",
    children=[
        html.Div(
            className="graph-header",
            children=[
                html.H1(
                    className="graph-title", children=["Mobility indicators in EU"]
                )
            ],
        ),
        dcc.Graph(
            id="heat_map"#,
            #config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
)



# The app itself



satellite_dropdown_text = html.H1(
    id="satellite-dropdown-text", children=["Moving with COVID-19"]
)

satellite_title = html.H1(id="satellite-name", children="")

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=["How did EU communities change their mobility with COVID-19?"]
)



map_graph = html.Div(
    id="world-map-wrapper",
    children=[
        html.Div(
            className="graph-header",
            children=[
                html.H1(
                    className="graph-title", children=["COVID-19 in EU"]
                )
            ],
        ),
        dcc.Graph(
            id="map_graph"#,
            #config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
)



graph = html.Div(
    id="histogram-container",
    children=[
        html.Div(
            className="graph-header",
            children=[
                html.H1(
                    className="graph-title", children=["How is mobility change impacting COVID-19 numbers?",dropdown_2]
                )
            ],
        ),
        dcc.Graph(id='graph2'),
    ],
)

# Control panel + map
main_panel_layout = dbc.Container(
    id="panel-upper-lower",
    fluid=True,
    children=[
        dcc.Interval(id="interval", interval=1 * 2000, n_intervals=0),
        dbc.Row(dbc.Col(glossary_2),className="pad-bottom"),
        html.Div(
                className="panel-lower sticky",
                children=[
                    dbc.Row(
                    [
                        dbc.Col(dropdown_country,width=2),
                        dbc.Col(slider_container,width=8),
                        dbc.Col(deaths_cases_toggle,width=2)
                    ],className="center-align")]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(
                    className="panel-lower",
                    children=[map_graph]
                ),width=6),
                dbc.Col(
                [
                    dbc.Row([dbc.Col(num_cases_cum),dbc.Col(num_deaths_cum)],className="pad-bottom"),
                    dbc.Row(dbc.Col(heatmap_section))
                ],width=6)
            ],className="pad-bottom"
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(className="panel-lower",children=[graph]),width=6),
                dbc.Col(glossary,width=6),
            ],className="pad-bottom")
    ],
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        html.Div(id="title_div",children=[
            satellite_dropdown_text,
            satellite_body,
        ]
        )
    ],
)

root_layout = html.Div(
    id="root",
    children=[
        html.Nav(id="navbar"),
        #dcc.Store(id="store-placeholder"),
        # For the case no components were clicked, we need to know what type of graph to preserve
        #dcc.Store(id="store-data-config", data={"info_type": "", "satellite_type": 0}),
        side_panel_layout,
        main_panel_layout,
        dcc.Markdown("Flag icons made by Freepik from www.flaticon.com")
    ]
)
app.layout = root_layout

@app.callback(
    Output('graph2', 'figure'),
    [Input('country_drop', 'value'),
     Input('indicators_multiple', 'value'),
     Input('control-panel-toggle-line', 'value')]
)
def update_graph2(country,indicators,btn):
    import plotly.express as px
    df = getCountryDf(country)
    df = df.set_index("date")
    df = df.groupby(pd.Grouper(freq='7D')).mean()
    df_indicators = df[indicators]
    
    if not btn:
        df_cases = df['new_cases']
        label = "New cases"
    else:
        df_cases = df['new_deaths']
        label = "New deaths"

    scatters = []
    for indicator in indicators:
        trace1 = go.Scatter(
            x = df_indicators.index,
            y = df_indicators[indicator],
            name=indicators_map[indicator],
            #marker_color='rgb(82, 106, 131)',
            yaxis='y2'
        )
        scatters.append(trace1)

    bar_chart = go.Bar(
        x= df_cases.index,
        y =df_cases,
        marker_color="#fec036",
        name=label+' daily'
    )


    ex2_layout = go.Layout(
        yaxis=dict(
            title=label,
            showgrid= False
        ),
        yaxis2=dict(
            title='Movement percentage change',
            overlaying='y',
            side='right',
            showgrid= False,
            zeroline= False
        ),
        xaxis=dict(
            tickmode='auto',
            nticks=16,
            tickangle = -25,
            gridcolor= "#636363",
            showline= False,
            ),
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="right",
            x=1
        ),
        font= {"color": "gray"},
        margin={'t': 0},

    )


    ex2_data = [bar_chart]
    ex2_data.extend(scatters)

    return go.Figure(data=ex2_data, layout=ex2_layout)




@app.callback(
    Output('map_graph', 'figure'),
    [Input('country_drop', 'value'),Input('map_slider', 'value'),Input('control-panel-toggle-line', 'value')]
)
def create_map(country,slider_time,btn):
    date = unixToDatetime(slider_time)
    if not btn:
        col = "new_cases_per_million"
        label = "new cases per million"
    else:
        col = "new_deaths_per_million"
        label = "new deaths per million"
    ctx = dash.callback_context
    country_time_df = df.rename(columns={'iso_code':'iso_a3'}).reset_index()
    country_df = country_time_df[country_time_df['date'] == date]
    vals = [0,1,2,3,5,6,7,8]
    exp_vals = [str(round(n)) for n in np.exp(vals)]
    map_europe_cases = go.Choroplethmapbox(
                        geojson=map_json,
                        locations=country_df['iso_a3'],
                        featureidkey='properties.iso_a3',
                        text = country_df['country_region'],
                        z=np.log(country_df[col].replace(0,1)),
                        #locationmode='ISO-3',
                        colorscale = 'Reds',
                        autocolorscale=False,
                        marker_line_color='darkgray',
                        marker_line_width=0.5,
                        colorbar_title = 'Number '+label,
                        zmin=0,
                        zmax=8,
                        customdata=country_df[col],
                        hovertemplate="<b>%{text}</b><br>%{customdata:0.1f} " + label,
                        colorbar=dict(
                            tickvals = vals ,
                            ticktext = exp_vals
                            )
                        )
    
    curr_country_df = getCountryDf(country)
    lat = curr_country_df.iloc[0]['latitude']
    lng = curr_country_df.iloc[0]['longitude']
    layout = dict(
        #title_text='Number of cases per Milion',
        geo={
            'resolution': 50,
            'scope': 'europe',
            'showframe' : False,
            'projection_type' : 'kavrayskiy7',
            'showland':False,
            'showlakes':False,
            "showcountries": False

        },
        mapbox={
            "accesstoken": MAPBOX_ACCESS_TOKEN,
            "style": MAPBOX_STYLE,
            "center": {"lat":lat,"lon":lng},
            "zoom":3
        },
        paper_bgcolor= "#2b2b2b",
        plot_bgcolor= "#2b2b2b",
        #mapbox_style="carto-positron",
        height=650,
        font= {"color": "gray"},
        margin={'t': 0,'b':0,'l':0,'r':0},
    )


    fig = go.Figure(data=map_europe_cases, layout=layout)
    return fig


@app.callback(
    Output('new_cases_in', 'children'),
    [Input('country_drop', 'value')],
)
def new_cases_in(country):
    return getCountryDf(country)['new_cases'].sum()


@app.callback(
    Output('new_deaths_in', 'children'),
    [Input('country_drop', 'value')],
)
def new_deaths_in(country):
    return getCountryDf(country)['new_deaths'].sum()


@app.callback(
    Output('slider_label', 'children'),
    [Input('map_slider', 'value')],
)

def updateLabel(val):
    return str(unixToDatetime(val).date())

#@app.callback(
#    Output('line_chart', 'figure'),
#    [Input('country_drop', 'value'),Input('control-panel-toggle-line', 'value')],
#)


def update_line_chart(country,btn):
    df = getCountryDf(country)
    df = df.set_index("date")
    df.index = pd.to_datetime(df.index)
    df = df.groupby(pd.Grouper(freq='3D')).mean()
    scatters = []

    if not btn:
        trace1 = go.Scatter(
            x = df.index,
            y = df["new_cases_per_million"],
            name="New cases",
            marker_color="#fec036",
        )
        scatters.append(trace1)
    else:
        trace2 = go.Scatter(
            x = df.index,
            y = df["new_deaths_per_million"],
            name="New Deaths",
            marker_color="#fec036"
        )
        scatters.append(trace2)

    ex2_layout = go.Layout(
        yaxis=dict(
            title='Per million',
            showgrid= False
        ),
        xaxis=dict(
            tickmode='auto',
            nticks=16,
            tickangle = -25,
            gridcolor= "#636363",
            showline= False,
            ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font= {"color": "gray"},
        margin={'t': 0},
    )

    #fig['layout'].update(barmode='stack')
    return go.Figure(data=scatters, layout=ex2_layout)

#@app.callback(
#    Output('map_graph', 'figure'),
#    [Input("map_slider", "value")],
#    [State('map_graph', 'figure')]
#)
#def update_map(value,fig):
#    fig.update_layout(z=df[df['date']==value])
#


@app.callback(
    Output('flag', 'children'),
    [Input('country_drop', 'value')],
)

def update_flag(country):
    code = df[df.country_region == country].iloc[0]['iso_code']
    return html.Img(src=app.get_asset_url("flags/"+code+".svg"),style ={"paddingRight":"10px"},height="40px")


@app.callback(
    Output('heat_map', 'figure'),
    [Input('map_slider', 'value')],
)
def update_heat_map(time):
    time = unixToDatetime(time)
    country_time_df = df
    country_df = country_time_df[country_time_df['date'] == time]
    
    indicators = [col for col in country_df.columns if col in indicators_map.keys()]
    heatmap = go.Heatmap(
                x=[indicators_map[indicator] for indicator in indicators],
                y=country_df["country_region"],
                z=country_df[indicators],
                colorscale="YlOrBr",
                )
    
    layout = dict(
        #title_text='Number of cases per Milion',
        paper_bgcolor= "#2b2b2b",
        plot_bgcolor= "#2b2b2b",
        #mapbox_style="carto-positron",
        #width=800,
        #height=600,
        font= {"color": "gray"},
        margin={'t': 0,'b':0,'l':0,'r':0},
    )
    
    
    return go.Figure(data=heatmap, layout=layout)
server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
