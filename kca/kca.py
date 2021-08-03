# Nicholas Eterovic 2021Q3
####################################################################################################

# Open-source packages.
import os
import json
import math
import gzip
import numpy as np
import pandas as pd
import typing as tp
import pykalman as pk
import plotly.colors as pcl
import plotly.subplots as psp

# Dash imports.
import dash
import dash.exceptions as dex
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_bootstrap_components as dbc

####################################################################################################
# LAYOUT

app_layout = [
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown('''
                # Kinetic Component Analysis (KCA)
                ***

                ### Introduction
                ***

                  This project is an implementation of a 2016
                [paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2422183)
                by Marcos Lopez de Prado and Riccardo Rebonato.

                  The authors introduce **Kinetic Component Analysis**,
                *"a state-space application that extracts the signal from a series
                of noisy measurements by applying a Kalman Filter on a Taylor expansion
                of a stochastic process"*.  

                  For long I've been interested in the application of Kalman Filters in finance,
                an industry infamous for exhibiting low signal-to-noise ratio in its data.

                  Moreover, I find the model pleasingly interpretable -
                decomposing an asset price's dynamics into familiar concepts:
                position, velocity, and acceleration.

                  Practitioners of technical analysis often speak of *trend* and *momentum*,
                concepts which are rigorously defined and quantified in the KCA model.

                  The aim of this project is to apply and evaluate the KCA model
                via an asset price prediction and execution problem.

                  Let's begin!
            '''),
        ]),
    ]),
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown('''
                ### Preparing the Data
                ***

                  The raw data set consists of trades in two assets: **MCU30** and **HGN9**,
                including the fields: `TIMESTAMP`, `PRICE`, and `SIZE`.

                  The objective is to forecast the assets' price evolution -
                the first step is to establish the precise time series.
                
                  The decided-on approach is to resample the trades into *volume bars*,
                where each bar summarizes trades with volume totalling a prespecified number -
                100 contracts, say.
                
                Each bar includes the aggregated fields `TIMESTAMP_first`, `TIMESTAMP_last`, `SIZE_sum`, `NOTIONAL_sum`, and `VWAP`.
                  The *volume-weighted average price (VWAP)* will be our target for price-prediction.

                  The sampling approach is motivated by volume as a *proxy for market information*.
                Hence, the price series will sample more (fewer) points during periods of heightened (lessened) market activity.

                  From a modelling perspective, this is attractive for multiple reasons:

                  * *Price-changes have reduced heteroskedasticity*.
                    Sampling in tandem with market activity produces more consistent price-change magnitudes.

                  * *Price-discontinuities are removed*.
                    Sampling with volume ensures at least one trade per bar, avoiding price-jumps across empty bars.

                  * *Price-series are more reliable*. Aggregated in every VWAP data point is a constant (volume) sample of trades. 

                However, the sampling approach also has drawbacks:

                  * *Price-changes are less interpretable*. The model views price evolving in volume - not chronological - time.

                  * *Price-forecasts will require volume-forecasts*. A seperate model for volume (bars) will be necessary.

                The resampled volume bars are viewable below, after **selecting an asset** and **clicking Load**.
            '''),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dcc.Markdown('''
                ### Visualizing the VWAP
                ***
            '''),
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=dbc.Button(
                            children='VWAP Data',
                            n_clicks=0,
                            color='dark',
                            disabled=True,
                        ),
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Trade Data:',
                    ),
                    dbc.Select(
                        id='select-kca-data-code',
                        options=[
                            {'label':'MCU30', 'value':'MCU30'},
                            {'label':'HGN9', 'value':'HGN9'},
                        ],
                        value=None,
                        placeholder='<Select Future>',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Volume per Bar:',
                    ),
                    dbc.Select(
                        id='select-kca-bars-delv',
                        options=[
                            {'label':f'{delv} Contracts', 'value':delv}
                            for delv in (100, 250, 500)
                        ],
                        value=100,
                        placeholder='<Select VBAR>',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='View Analysis In:',
                    ),
                    dbc.Select(
                        id='select-kca-bars-time',
                        options=[
                            {'label':'Volume Time', 'value':'VBAR'},
                            {'label':'Chronological Time', 'value':'TIMESTAMP_last'},
                        ],
                        value='VBAR',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Log Price?',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=dbc.Checkbox(
                            id='checkbox-kca-bars-plog',
                            checked=False,
                            disabled=False,
                        ), 
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Price Difference?',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=dbc.Checkbox(
                            id='checkbox-kca-bars-diff',
                            checked=False,
                            disabled=False,
                        ), 
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Cumulate Volume?',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=dbc.Checkbox(
                            id='checkbox-kca-bars-cums',
                            checked=False,
                            disabled=False,
                        ), 
                    ),
                    dbc.InputGroupAddon(
                        addon_type='append',
                        children=dbc.Button(
                            id='button-kca-bars-load',
                            children='Load',
                            n_clicks=0,
                            color='primary',
                            disabled=True,
                        ),
                    ),
                ],
            ),
        ]),
        dcc.Store(id='store-kca-bars', data=[]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(width=6, children=[
                    dcc.Graph(
                        id='graph-kca-bars-vwap',
                        config={'displayModeBar':False, 'displaylogo':False},
                        figure=psp.make_subplots(
                            rows=1,
                            cols=2,
                            shared_yaxes=False,
                            column_widths=[2/3, 1/3],
                            x_title='Time',
                            y_title='VWAP',
                            subplot_titles=[
                                'Volume-Weighted-Average-Price (VWAP) by Time',
                                'Distribution',
                            ],
                        ),
                    ),
                ]),
                dbc.Col(width=6, children=[
                    dcc.Graph(
                        id='graph-kca-bars-volume',
                        config={'displayModeBar':False, 'displaylogo':False},
                        figure=psp.make_subplots(
                            rows=1,
                            cols=2,
                            shared_yaxes=False,
                            column_widths=[2/3, 1/3],
                            horizontal_spacing=0.05,
                            x_title='Time',
                            y_title='Volume',
                            subplot_titles=[
                                'Volume by Time',
                                'Distribution',
                            ],
                        ),
                    ),
                ]),
            ]),
        ]),
    ]),
    dcc.Store(id='store-kca-filt', data={}),
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children=dbc.Button(
                            children='KCA Model',
                            n_clicks=0,
                            color='dark',
                            disabled=True,
                        ),
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='Degree:',
                    ),
                    dbc.Input(
                        id='input-kca-filt-pow',
                        debounce=False,
                        value=0,
                        type='number',
                        min=0,
                        max=3,
                        step=1,
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='State Covariance Seed:',
                    ),
                    dbc.Input(
                        id='input-kca-filt-seed',
                        debounce=False,
                        value=1e-3,
                        type='number',
                    ),
                    dbc.InputGroupAddon(
                        addon_type='prepend',
                        children='EM Iterations:',
                    ),
                    dbc.Input(
                        id='input-kca-filt-iter',
                        debounce=False,
                        value=1,
                        type='number',
                        min=1,
                        step=1,
                    ),
                    dbc.InputGroupAddon(
                        addon_type='append',
                        children=dbc.Button(
                            id='button-kca-filt-fit',
                            children='Fit',
                            n_clicks=0,
                            color='primary',
                            disabled=True,
                        ),
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dbc.Textarea(
                id='textarea-kca-filt',
                value='',
                placeholder='Trade Data Required',
                spellCheck=False,
                bs_size='sm',
                disabled=True,
                style={'height':'50vh'},
            ),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            'State Estimate Analysis',
        ]),
        dbc.CardBody([
            dcc.Graph(
                id='graph-kca-smooth',
                config={'displayModeBar':False, 'displaylogo':False},
                figure=psp.make_subplots(
                    rows=1,
                    cols=2,
                    shared_yaxes=False,
                    column_widths=[2/3, 1/3],
                    x_title='Time',
                    y_title='Smoothed State',
                    subplot_titles=[
                        'Smoothed States by Time',
                        'Distribution',
                    ],
                ),
            ),
            dcc.Graph(
                id='graph-kca-filter',
                config={'displayModeBar':False, 'displaylogo':False},
                figure=psp.make_subplots(
                    rows=1,
                    cols=2,
                    shared_yaxes=False,
                    column_widths=[2/3, 1/3],
                    x_title='Time',
                    y_title='Filtered State',
                    subplot_titles=[
                        'Filtered States by Time',
                        'Distribution',
                    ],
                ),
            ),
            dcc.Graph(
                id='graph-kca-pred',
                config={'displayModeBar':False, 'displaylogo':False},
                figure=psp.make_subplots(
                    rows=1,
                    cols=2,
                    shared_yaxes=False,
                    column_widths=[2/3, 1/3],
                    x_title='Time',
                    y_title='Predicted State',
                    subplot_titles=[
                        'Predicted States by Time',
                        'Distribution',
                    ],
                ),
            ),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            'VWAP Prediction Analysis',
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(width=8, children=[
                    dcc.Graph(
                        id='graph-kca-error-cae',
                        config={'displayModeBar':False, 'displaylogo':False},
                        figure={
                            'data':[],
                            'layout':{
                                'title':'Cumulative Absolute Error',
                                'yaxis':{'title':'CAE'},
                                'xaxis':{'title':'Time'},
                            },
                        },
                    ),
                ]),
                dbc.Col(width=4, children=[
                    dcc.Graph(
                        id='graph-kca-error-dist',
                        config={'displayModeBar':False, 'displaylogo':False},
                        figure={
                            'data':[],
                            'layout':{
                                'title':'Error Distribution',
                                'yaxis':{'title':'Error Bin Count'},
                                'xaxis':{'title':'Error Bin'},
                                'barmode':'overlay',
                            },
                        },
                    ),
                ]),
            ]),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        [
            ddp.Output('button-kca-bars-load', 'children'),
            ddp.Output('button-kca-bars-load', 'color'),
            ddp.Output('button-kca-bars-load', 'disabled'),
        ],
        [
            ddp.Input('select-kca-data-code', 'value'),
            ddp.Input('select-kca-bars-delv', 'value'),
            ddp.Input('select-kca-bars-time', 'value'),
        ],
    )
    def set_load_state(*args:tp.Tuple[str]) -> tp.Tuple[str, str, bool]:
        if not all(args):
            return 'Load', 'primary', True
        return 'Load', 'primary', False

    @app.callback(
        [
            ddp.Output('store-kca-bars', 'data'),
            ddp.Output('graph-kca-bars-vwap', 'figure'),
            ddp.Output('graph-kca-bars-volume', 'figure'),
        ],
        [ddp.Input('button-kca-bars-load', 'n_clicks')],
        [
            ddp.State('select-kca-data-code', 'value'),
            ddp.State('select-kca-bars-delv', 'value'),
            ddp.State('select-kca-bars-time', 'value'),
            ddp.State('checkbox-kca-bars-plog', 'checked'),
            ddp.State('checkbox-kca-bars-diff', 'checked'),
            ddp.State('checkbox-kca-bars-cums', 'checked'),
            ddp.State('graph-kca-bars-vwap', 'figure'),
            ddp.State('graph-kca-bars-volume', 'figure'),
        ],
    )
    def load_data(
        n_clicks:int,
        code:str,
        delv:str,
        time:str,
        plog:bool,
        diff:bool,
        cums:bool,
        *figures:tp.List[dict],
    ) -> tp.List[dict]:
        if not n_clicks:
            raise dex.PreventUpdate
        for figure in figures:
            figure.update({'data':[]})
        if not code or not delv or not time:
            return ([], *figures)
        try:
            bars_file = os.path.join('data', 'ticks', f'{code}.bars.{delv}.gz')
            if os.path.exists(path=bars_file):
                # Load pre-aggregated volume-bar data.
                dtype = {
                    'VBAR':'int',
                    'TIMESTAMP_first':'datetime64[ns]',
                    'TIMESTAMP_last':'datetime64[ns]',
                    'NOTIONAL_sum':'float',
                    'SIZE_sum':'int',
                    'VWAP':'float',
                }
                usecols = list(dtype.keys())
                bars = pd.read_csv(filepath_or_buffer=bars_file, usecols=usecols)
                bars = bars.astype(dtype=dtype, errors='raise')
            else:
                # Load trade data.
                trd2_file = os.path.join('data', 'ticks', f'{code}.trd2.gz')
                usecols = ['TIMESTAMP', 'PRICE', 'SIZE']
                trd2 = pd.read_csv(filepath_or_buffer=trd2_file, usecols=usecols)
                trd2 = trd2.loc[lambda df:df['TIMESTAMP'].ne(f'DATA_QUALITY_CHANGE:{code}')]
                # Enforce data types.
                delv = int(delv)
                trd2['PRICE'] = trd2['PRICE'].astype(float)
                trd2['SIZE'] = trd2['SIZE'].astype(int)
                trd2['TIMESTAMP'] = pd.to_datetime(arg=trd2['TIMESTAMP'].astype(str), format='%Y%m%d%H%M%S.%f')
                # Resample trade data into volume-bars.
                trd2['NOTIONAL'] = trd2['PRICE']*trd2['SIZE']
                by = trd2['SIZE'].cumsum().floordiv(delv).mul(delv).rename('VBAR')
                func = {'TIMESTAMP':['first', 'last'], 'NOTIONAL':'sum', 'SIZE':'sum'}
                bars = trd2.groupby(by=by).agg(func=func)
                bars.columns = bars.columns.map('_'.join)
                bars.reset_index(level='VBAR', drop=False, inplace=True)
                bars['VWAP'] = bars['NOTIONAL_sum']/bars['SIZE_sum']
                # Save aggregated volume-bar data.
                bars.to_csv(path_or_buf=bars_file, index=False)

            # Return volume-bar records.
            records = bars.to_dict(orient='records')
            colors = pcl.DEFAULT_PLOTLY_COLORS
            for i, (col, figure) in enumerate(zip(['VWAP', 'SIZE_sum'], figures)):
                # Reset layout.
                figure['layout'].update({'template':None})
                for axis in ('xaxis', 'yaxis'):
                    for key in ('type', 'range', 'autorange'):
                        figure['layout'][axis].pop(key, None)
                # Extract data.
                y = bars[col]
                x = bars[time]
                color = colors[i%len(colors)]
                # Apply transformations.
                if col=='VWAP':
                    if plog:
                        y = np.log(y)
                    if diff:
                        y = y.diff()
                else:
                    if cums:
                        y = y.cumsum()
                # Visualize data.
                figure.update({'data':[
                    {
                        'type':'scatter',
                        'y':y,
                        'x':x,
                        'xaxis':'x',
                        'yaxis':'y',
                        'name':col.split('_')[0],
                        'legendgroup':col,
                        'showlegend':True,
                        'connectgaps':False,
                        'line':{'color':color},
                    },
                    {
                        'type':'box',
                        'y':y,
                        'xaxis':'x2',
                        'yaxis':'y2',
                        'name':col.split('_')[0],
                        'legendgroup':col,
                        'showlegend':False,
                        'boxmean':'sd',
                        'boxpoints':False,
                        'line':{'color':color},
                        'marker':{'color':color},
                    },
                ]})
            return (records, *figures)
        except Exception as exception:
            print(str(exception))
            return ([], *figures)

    @app.callback(
        [
            ddp.Output('button-kca-filt-fit', 'children'),
            ddp.Output('button-kca-filt-fit', 'color'),
            ddp.Output('button-kca-filt-fit', 'disabled'),
        ],
        [
            ddp.Input('store-kca-bars', 'data'),
            ddp.Input('input-kca-filt-pow', 'value'),
            ddp.Input('input-kca-filt-seed', 'value'),
            ddp.Input('input-kca-filt-iter', 'value'),
        ],
    )
    def set_fit_state(records:tp.List[dict], pow:int, seed:float, iter:str) -> tp.Tuple[str, str, bool]:
        if not all([records, seed, iter]) or not isinstance(pow, int) or not isinstance(iter, int):
            return 'Fit', 'primary', True
        return 'Fit', 'primary', False

    @app.callback(
        [
            ddp.Output('store-kca-filt', 'data'),
            ddp.Output('textarea-kca-filt', 'value'),
        ],
        [ddp.Input('button-kca-filt-fit', 'n_clicks')],
        [
            ddp.State('store-kca-bars', 'data'),
            ddp.State('select-kca-bars-time', 'value'),
            ddp.State('input-kca-filt-pow', 'value'),
            ddp.State('input-kca-filt-seed', 'value'),
            ddp.State('input-kca-filt-iter', 'value'),
        ],
    )
    def fit_filt(n_clicks:int, records:tp.List[dict], time:str, pow:int, seed:float, iter:int) -> dict:
        if not n_clicks:
            raise dex.PreventUpdate
        if not all([records, seed, iter]) or not isinstance(pow, int) or not isinstance(iter, int):
            return {}, ''
        try:
            # Retrieve VWAP and VBAR data.
            bars = pd.DataFrame(data=records)
            dv = bars['SIZE_sum'].mean()
            X = bars[['VWAP']]
            # Specify Kalman Filter model.
            states = range(pow+1)
            A = [[0 if i>j else dv**(j-i)/math.factorial(j-i) for j in states] for i in states]
            C = [[1 if i==0 else 0 for i in states]]
            Q = [[0 if i!=j else seed**i if seed<0 else seed**-i if i==j else 0 for j in states] for i in states]
            z = [X.iloc[0, 0] if i==0 else 0 for i in states]
            em_vars = ['transition_covariance', 'observation_covariance']
            kf = pk.KalmanFilter(
                transition_matrices=A,
                transition_covariance=None,
                observation_matrices=C,
                observation_covariance=None,
                initial_state_mean=z,
                initial_state_covariance=Q,
                em_vars=em_vars,
            )
            # Apply Expectation Maximization to estimate remaining parameters.
            kf.em(X=X, n_iter=iter, em_vars=em_vars)
            # Extrat model specification.
            text = json.dumps(obj=kf.__dict__, indent=4, default=lambda x:list(x) if pd.api.types.is_list_like(x) else float(x))
            filt = json.loads(s=text)
            return filt, text
        except Exception as exception:
            print(str(exception))
            return {}, ''

    @app.callback(
        [
            ddp.Output('graph-kca-smooth', 'figure'),
            ddp.Output('graph-kca-filter', 'figure'),
            ddp.Output('graph-kca-pred', 'figure'),
        ],
        [ddp.Input('store-kca-filt', 'data')],
        [
            ddp.State('store-kca-bars', 'data'),
            ddp.State('select-kca-bars-time', 'value'),
            ddp.State('graph-kca-smooth', 'figure'),
            ddp.State('graph-kca-filter', 'figure'),
            ddp.State('graph-kca-pred', 'figure'),
        ],
    )
    def plot_filt(cfg:dict, records:tp.List[dict], time:str, *figures:tp.List[dict]) -> dict:
        if not cfg:
            raise dex.PreventUpdate
        for figure in figures:
            figure.update({'data':[]})
        if not all([records, time]):
            return figures
        try:
            # Retrieve VWAP and VBAR data.
            bars = pd.DataFrame(data=records)
            X = bars[['VWAP']]
            # Specify Kalman Filter model.
            kf = pk.KalmanFilter(**cfg)
            # Clean figures.
            colors = pcl.DEFAULT_PLOTLY_COLORS
            for figure in figures:
                # Reset layout.
                figure['layout'].update({'template':None})
                for axis in ('xaxis', 'yaxis'):
                    for key in ('type', 'range', 'autorange'):
                        figure['layout'][axis].pop(key, None)
                # Renew data.
                color = colors[0]
                figure.update({'data':[
                    {
                        'type':'scatter',
                        'y':bars['VWAP'],
                        'x':bars[time],
                        'xaxis':'x',
                        'yaxis':'y',
                        'name':'Observed VWAP',
                        'legendgroup':'VWAP',
                        'showlegend':True,
                        'connectgaps':False,
                        'line':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    },
                    {
                        'type':'box',
                        'y':bars['VWAP'],
                        'xaxis':'x2',
                        'yaxis':'y2',
                        'name':'Observed VWAP',
                        'legendgroup':'VWAP',
                        'showlegend':False,
                        'boxmean':'sd',
                        'boxpoints':False,
                        'line':{'color':color},
                        'marker':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    },
                ]})
            # Construct smoothed state figures.
            Z, V = kf.smooth(X=X)
            V = np.array(list(map(np.diag, V)))
            for i, (z, v) in enumerate(zip(Z.T, V.T)):
                color = colors[(i+1)%len(colors)]
                figures[0]['data'].extend([
                    {
                        'type':'scatter',
                        'fill':'tonexty',
                        'y':z+dev*v**.5,
                        'x':bars[time],
                        'xaxis':'x',
                        'yaxis':'y',
                        'name':f'Smoothed Degree {i} (M{dev:+.0f}SD)',
                        'legendgroup':i,
                        'showlegend':dev==0,
                        'visible':True if i==0 else 'legendonly',
                        'connectgaps':False,
                        'line':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    }
                    for dev in (-1, 0, 1)
                ] + [
                    {
                        'type':'box',
                        'y':z,
                        'xaxis':'x2',
                        'yaxis':'y2',
                        'name':f'Smoothed Degree {i}',
                        'legendgroup':i,
                        'showlegend':False,
                        'visible':True if i==0 else 'legendonly',
                        'boxmean':'sd',
                        'boxpoints':False,
                        'line':{'color':color},
                        'marker':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    },
                ])
            # Construct filtered state figures.
            Z, V = kf.filter(X=X)
            V = np.array(list(map(np.diag, V)))
            for i, (z, v) in enumerate(zip(Z.T, V.T)):
                color = colors[(i+1)%len(colors)]
                figures[1]['data'].extend([
                    {
                        'type':'scatter',
                        'fill':'tonexty',
                        'y':z+dev*v**.5,
                        'x':bars[time],
                        'xaxis':'x',
                        'yaxis':'y',
                        'name':f'Filtered Degree {i} (M{dev:+.0f}SD)',
                        'legendgroup':i,
                        'showlegend':dev==0,
                        'visible':True if i==0 else 'legendonly',
                        'connectgaps':False,
                        'line':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    }
                    for dev in (-1, 0, +1)
                ] + [
                    {
                        'type':'box',
                        'y':z,
                        'xaxis':'x2',
                        'yaxis':'y2',
                        'name':f'Filtered Degree {i}',
                        'legendgroup':i,
                        'showlegend':False,
                        'visible':True if i==0 else 'legendonly',
                        'boxmean':'sd',
                        'boxpoints':False,
                        'line':{'color':color},
                        'marker':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    },
                ])
            # Construct predicted state figures.
            A = np.array(kf.transition_matrices)
            Z = np.array(list(map(A.dot, Z)))
            for i, (z, v) in enumerate(zip(Z.T, V.T)):
                color = colors[(i+1)%len(colors)]
                figures[2]['data'].extend([
                    {
                        'type':'scatter',
                        'fill':'tonexty',
                        'y':z+dev*v**.5,
                        'x':bars[time],
                        'xaxis':'x',
                        'yaxis':'y',
                        'name':f'Predicted Degree {i} (M{dev:+.0f}SD)',
                        'legendgroup':i,
                        'showlegend':dev==0,
                        'visible':True if i==0 else 'legendonly',
                        'connectgaps':False,
                        'line':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    }
                    for dev in (-1, 0, 1)
                ] + [
                    {
                        'type':'box',
                        'y':z,
                        'xaxis':'x2',
                        'yaxis':'y2',
                        'name':f'Predicted Degree {i}',
                        'legendgroup':i,
                        'showlegend':False,
                        'visible':True if i==0 else 'legendonly',
                        'boxmean':'sd',
                        'boxpoints':False,
                        'line':{'color':color},
                        'marker':{'color':color},
                        'hoverlabel':{'namelength':-1},
                    },
                ])
            return figures
        except Exception as exception:
            print(str(exception))
            return figures

    @app.callback(
        [
            ddp.Output('graph-kca-error-cae', 'figure'),
            ddp.Output('graph-kca-error-dist', 'figure'),
        ],
        [ddp.Input('graph-kca-pred', 'figure')],
        [
            ddp.State('graph-kca-error-cae', 'figure'),
            ddp.State('graph-kca-error-dist', 'figure'),
        ],
    )
    def load_error(pred:dict, *figures:tp.List[dict]) -> dict:
        pred.setdefault('data', [])
        for figure in figures:
            figure.update({'data':[]})
        vwap = [datum for datum in pred['data'] if datum['legendgroup']=='VWAP']
        pred = [datum for datum in pred['data'] if datum['legendgroup']==0 and '0' in datum['name']]
        if not vwap or not pred:
            return figures
        figures[0]['data'].extend([
            {
                'type':'scatter',
                'x':vwap[0]['x'][1:],
                'y':np.cumsum(np.abs(np.subtract(vwap[0]['y'][:-1], vwap[0]['y'][1:]))),
                'name':'Martingale Prediction (Benchmark)',
                'hoverlabel':{'namelength':-1},
                'fill':'tozeroy',
            },
            {
                'type':'scatter',
                'x':vwap[0]['x'][1:],
                'y':np.cumsum(np.abs(np.subtract(pred[0]['y'][1:], vwap[0]['y'][1:]))),
                'name':pred[0]['name'],
                'hoverlabel':{'namelength':-1},
                'fill':'tozeroy',
            },
        ])
        figures[1]['data'].extend([
            {
                'type':'histogram',
                'x':np.subtract(vwap[0]['y'][:-1], vwap[0]['y'][1:]),
                'name':'Martingale Prediction (Benchmark)',
                'hoverlabel':{'namelength':-1},
                'opacity':0.5,
            },
            {
                'type':'histogram',
                'x':np.subtract(pred[0]['y'][1:], vwap[0]['y'][1:]),
                'name':pred[0]['name'],
                'hoverlabel':{'namelength':-1},
                'opacity':0.5,
            },
        ])
        return figures
