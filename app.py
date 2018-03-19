import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
from plotly.graph_objs import *
#from flask import Flask
#from flask_cors import CORS
import pandas as pd
import numpy as np
#import os

app = dash.Dash('CrimeApp')
server = app.server

#if 'DYNO' in os.environ:
#    app.scripts.append_script({
#        'external_url': #'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c#44ab/plotly_ga.js'
#    })

mapbox_access_token = 'pk.eyJ1IjoibnNoYXBvc2giLCJhIjoiY2plb2k5d2c0NXBjbDJxbzFuZ3R5Zzh1ZSJ9.wwvkxshl2uid_4wbMbnbQA'


#df = pd.read_pickle("dccrimes.pkl")    

#df = pd.read_csv('Crime_incidents_in_2017.csv')
df = pd.read_csv('https://s3.amazonaws.com/iamdatascientist.org/data/Crime_Incidents_in_2017.csv')
df["Date/Time"] = pd.to_datetime(df["REPORT_DAT"], format="%Y-%m-%dT%H:%M:%S")
dt = np.timedelta64(1,'D')
d0 = np.datetime64("2017-01-01")
df["dayofyear"] = [(d - d0)/dt for d in df["Date/Time"]]
df.index = df["Date/Time"]
df['hover_text'] = ["{}\n{}".format(r['Date/Time'],r['OFFENSE']) for i,r in df.iterrows()]
#df.to_pickle("dccrimes.pkl")    

months = {
        'Jan':0,
        'Feb':1,
        'Mar':2,
        'Apr': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'Aug': 8,
        'Sept': 9,
        'Oct':10,
        'Nov':11,
        'Dec':12
    }

def getValue(value):
    val = {
        'Jan':31,
        'Feb':28,
        'Mar':31,
        'Apr': 30,
        'May': 31,
        'June': 30,
        'July': 31,
        'Aug': 31,
        'Sept': 30,
        'Oct':31,
        'Nov':30,
        'Dec':31
    }[value]
    return val

def range_slider_ticks():

    marks = {}
    day = 0
    for m in months:
        nd = getValue(m)
        marks.update({day: '{}'.format(m)})
        day += nd
    return marks

app.layout = html.Div([
    html.Div([

            html.Div([
                        
            html.Div([
                dcc.Markdown("Source: [http://opendata.dc.gov](http://opendata.dc.gov)")
            ]),
            html.H2("DC Crimes - 2017", style={'font-family': 'Dosis'}),
            html.P(id='total-rides-selection', className="totalRideSelection"),
            html.P("Select different dates using the slider\
                        below and hours by selecting different time frames on the\
                        histogram",style={'font-family': 'Dosis'} ),
            dcc.RangeSlider(
                    id="range-slider",
                    min=1,
                    max=365,
                    step=1,
                    value=[1,365],
                    marks = range_slider_ticks(),
                    className="bars"
                ),             
            html.P(id='date-value', className="dateValue"),
            html.P(id='total-crimes', className="totalRides"),

            html.Div([
                html.Div([
                ]),
                html.P("Select different days using the dropdown and the slider\
                        below or by selecting different time frames on the\
                        histogram", className="explanationParagraph twelve columns"),

                dcc.Graph(id='map-graph'),

                dcc.Dropdown(
                    id='bar-selector',
                    options=[
                        {'label': '0:00', 'value': '0'},
                        {'label': '1:00', 'value': '1'},
                        {'label': '2:00', 'value': '2'},
                        {'label': '3:00', 'value': '3'},
                        {'label': '4:00', 'value': '4'},
                        {'label': '5:00', 'value': '5'},
                        {'label': '6:00', 'value': '6'},
                        {'label': '7:00', 'value': '7'},
                        {'label': '8:00', 'value': '8'},
                        {'label': '9:00', 'value': '9'},
                        {'label': '10:00', 'value': '10'},
                        {'label': '11:00', 'value': '11'},
                        {'label': '12:00', 'value': '12'},
                        {'label': '13:00', 'value': '13'},
                        {'label': '14:00', 'value': '14'},
                        {'label': '15:00', 'value': '15'},
                        {'label': '16:00', 'value': '16'},
                        {'label': '17:00', 'value': '17'},
                        {'label': '18:00', 'value': '18'},
                        {'label': '19:00', 'value': '19'},
                        {'label': '20:00', 'value': '20'},
                        {'label': '21:00', 'value': '21'},
                        {'label': '22:00', 'value': '22'},
                        {'label': '23:00', 'value': '23'}
                    ],
                    multi=True,
                    placeholder="Select certain hours using \
                                 the box-select/lasso tool or \
                                 using the dropdown menu",
                    className="bars"
                ),             
                dcc.Graph(id="histogram"),
                html.P("", id="popupAnnotation", className="popupAnnotation"),
            ], className="graph twelve coluns"),
        ], style={'margin': 'auto auto'}),

    ], className="graphSlider ten columns offset-by-one"),
], style={"padding-top": "20px"})



def getIndex(value):
    if(value==None):
        return 0
    return months[value]

def getClickIndex(value):
    if(value==None):
        return 0
    return value['points'][0]['x']



@app.callback(Output("bar-selector", "value"),
              [Input("histogram", "selectedData")])
def update_bar_selector(value):
    holder = []
    if(value is None or len(value) is 0):
        return holder
    for x in value['points']:
        holder.append(str(int(x['x'])))
    return holder


@app.callback(Output("total-crimes", "children"),
              [Input('range-slider', 'value'),Input('bar-selector', 'value')])
def update_total_crimes(day_range, selection):
    if len(selection) == 0:
        dff = df.loc[(df.dayofyear>day_range[0]) & (df.dayofyear<day_range[1]),:]
    else:
        selected_hours = [int(h) for h in selection]
        dff = df.loc[(df.dayofyear>day_range[0]) & (df.dayofyear<day_range[1]) & \
                     (np.isin(df.index.hour,selected_hours)),:]
    return ("Total # of incidents: {:,d}".format(len(dff)))



#@app.callback(Output("date-value", "children"),
#              [Input("my-dropdown", "value"), Input('my-slider', 'value'),
#               Input("bar-selector", "value")])
#def update_date(value, slider_value, selection):
#    holder = []
#    if(value is None or selection is None or len(selection) is 24
#       or len(selection) is 0):
#        return (value, " ", slider_value, " - showing: All")



@app.callback(Output("popupAnnotation", "children"),
              [Input("bar-selector", "value")])
def clear_selection(value):
    if(value is None or len(value) is 0):
        return "Select any of the bars to section data by time"
    else:
        return ""


def get_selection(day_range, selection):
    xVal = []
    yVal = []
    xSelected = []

    colorVal = ["#F4EC15", "#DAF017", "#BBEC19", "#9DE81B", "#80E41D", "#66E01F",
                "#4CDC20", "#34D822", "#24D249", "#25D042", "#26CC58", "#28C86D",
                "#29C481", "#2AC093", "#2BBCA4", "#2BB5B8", "#2C99B4", "#2D7EB0",
                "#2D65AC", "#2E4EA4", "#2E38A4", "#3B2FA0", "#4E2F9C", "#603099"]

    if(selection is not None):
        for x in selection:
            xSelected.append(int(x))
    for i in range(0, 24, 1):
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = ('#FFFFFF')
        xVal.append(i)
        dff = df.loc[(df.dayofyear>day_range[0]) & (df.dayofyear<day_range[1]) & \
                     (df.index.hour == i),:]
        yVal.append(len(dff))

    return [np.array(xVal), np.array(yVal), np.array(xSelected),
            np.array(colorVal)]



@app.callback(Output("histogram", "figure"),
              [Input('range-slider', 'value'),Input("bar-selector", "value")])
def update_histogram( day_range, selection):

    [xVal, yVal, xSelected, colorVal] = get_selection(day_range,selection)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode='group',
        margin=Margin(l=10, r=0, t=0, b=0),
        showlegend=False,
        plot_bgcolor='gray',
        paper_bgcolor='rgb(66, 134, 244, 0)',
        height=250,
        dragmode="select",
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00"
        ),
        yaxis=dict(
            range=[0, max(yVal)+max(yVal)/4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode='nonnegative',
            zeroline='hidden'
        ),
        annotations=[
            dict(x=xi, y=yi,
                 text=str(yi),
                 xanchor='center',
                 yanchor='bottom',
                 showarrow=False,
                 font=dict(
                    color='white'
                 ),
                 ) for xi, yi in zip(xVal, yVal)],
    )

    return go.Figure(
           data=Data([
                go.Bar(
                    x=xVal,
                    y=yVal,
                    marker=dict(
                        color=colorVal
                    ),
                    hoverinfo="x"
                ),
                go.Scatter(
                    opacity=0,
                    x=xVal,
                    y=yVal/2,
                    hoverinfo="none",
                    mode='markers',
                    marker=Marker(
                        color='rgb(66, 134, 244, 0)',
                        symbol="square",
                        size=40
                    ),
                    visible=True
                )
            ]), layout=layout)




@app.callback(Output("map-graph", "figure"),
              [Input('range-slider', 'value'),Input("bar-selector", "value")],
              [State('map-graph', 'relayoutData')])
def update_graph(day_range, selectedData, prevLayout):
    zoom = 11.0
    latInitial = 38.9072
    lonInitial = -77.0369
    bearing = 0

    if(prevLayout is not None):
        zoom = float(prevLayout['mapbox']['zoom'])
        latInitial = float(prevLayout['mapbox']['center']['lat'])
        lonInitial = float(prevLayout['mapbox']['center']['lon'])
        bearing = float(prevLayout['mapbox']['bearing'])

    if len(selectedData) == 0:
        dff = df.loc[(df.dayofyear>day_range[0]) & (df.dayofyear<day_range[1]),:]
    else:
        selected_hours = [int(h) for h in selectedData]
        dff = df.loc[(df.dayofyear>day_range[0]) & (df.dayofyear<day_range[1]) & \
                     (np.isin(df.index.hour,selected_hours)),:]
  
    
    return go.Figure(
        data=Data([
            Scattermapbox(
                lat=dfoff['LATITUDE'],
                lon=dfoff['LONGITUDE'],
                mode='markers',
                hoverinfo="text",
                name = "{}({})".format(off,str(len(dfoff))),
                text=dff.hover_text,
                marker=Marker(
                    color=np.append(np.insert(dfoff.index.hour, 0, 0), 23),
                    colorscale=[[0, "#F4EC15"], [0.04167, "#DAF017"],
                                [0.0833, "#BBEC19"], [0.125, "9DE81B"],
                                [0.1667, "#80E41D"], [0.2083, "#66E01F"],
                                [0.25, "#4CDC20"], [0.292, "#34D822"],
                                [0.333, "#24D249"], [0.375, "#25D042"],
                                [0.4167, "#26CC58"], [0.4583, "#28C86D"],
                                [0.50, "#29C481"], [0.54167, "#2AC093"],
                                [0.5833, "#2BBCA4"],
                                [1.0, "#613099"]],
                    opacity=0.7,
                    size=10,
                    symbol = 'circle',
                    colorbar=dict(
                        thicknessmode="fraction",
                        title="Time of<br>Day",
                        x=0.935,
                        xpad=0,
                        nticks=24,
                        tickfont=dict(
                            color='black'
                        ),
                        titlefont=dict(
                            color='black'
                        ),
                        titleside='left'
                        )
                ),
            ) for off,dfoff in dff.groupby("OFFENSE")
        ]),
        layout=Layout(
            autosize=True,
            height=750,
            margin=Margin(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(font=dict(size=10), orientation='h'),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(
                    lat=latInitial, # 40.7272
                    lon=lonInitial # -73.991251
                ),
                style='light',
                bearing=bearing,
                zoom=zoom
            ),
        )
    )


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]


for css in external_css:
    app.css.append_css({"external_url": css})




if __name__ == '__main__':
#   to run locally 
    app.run_server(debug=True)
#   for docker
#    app.run_server(debug=True,host='0.0.0.0',port=80)


