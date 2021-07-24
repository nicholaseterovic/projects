# Nicholas Eterovic 2021Q3
####################################################################################################

# Dash packages.
import dash
import dash_tabulator as dtb
import dash.exceptions as dex
import dash_pivottable as dpv
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as dhc
import dash_bootstrap_components as dbc

# Open-source packages
import numpy as np
import pandas as pd
import typing as tp
import plotly.data as ptd
import sklearn.utils as sku
import sklearn.datasets as skd

####################################################################################################
# LAYOUT

datasets = {
    'sklearn':{
        source:[func for func in dir(skd) if func.startswith(source)]
        for source in ['load', 'fetch', 'make']
    },
    'plotly':{
        'load':[func for func in dir(ptd) if not func.startswith('_')],
    },
}

app_layout = [
    dbc.Card([
        dbc.CardHeader([
            dbc.InputGroup(
                size='sm',
                children=[
                    dbc.DropdownMenu(
                        label='Load',
                        color='primary',
                        direction='right',
                        addon_type='append',
                        children=[
                            dbc.DropdownMenuItem(
                                children='Upload',
                                n_clicks=0,
                                disabled=True,
                            ),
                        ] + [
                            dbc.DropdownMenu(
                                label=library.capitalize(),
                                direction='right',
                                color='link',
                                disabled=(library=='sklearn'),
                                children=[
                                    dbc.DropdownMenu(
                                        label=source.capitalize(),
                                        direction='right',
                                        color='link',
                                        children=[
                                            dbc.DropdownMenuItem(
                                                id=f'pivot-dmi-{library}-{source}-{func}',
                                                children=func.split('_', maxsplit=1)[-1],
                                                disabled=(source=='fetch'),
                                                n_clicks=0,
                                            )
                                            for func in funcs
                                        ],
                                    )
                                    for source, funcs in sources.items()
                                ],
                            )
                            for library, sources in datasets.items()
                        ],
                    ),
                    dbc.Input(
                        type='text',
                        disabled=True,
                    ),
                ],
            ),
        ]),
        dbc.CardBody([
            dtb.DashTabulator(
                id='pivot-tabulator-raw',
                data=[],
                columns=[{
                    'title':'',
                    'field':'none',
                    'hozAlign':'center',
                    'headerSort':False,
                }],
                options={
                    'placeholder':'None',
                    'layout':'fitDataStretch',
                    'layoutColumnsOnNewData':False,
                    'minHeigh':'50vh',
                    'maxHeight':'50vh',
                    'height':'50vh',
                    'pagination':'local',
                    'selectable':False,
                },
            ),
        ]),
    ]),
    dbc.Card([
        dbc.CardBody([
            dhc.Div(id='pivot-div-agg', children=[]),
        ]),
    ]),
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    @app.callback(
        [
            ddp.Output('pivot-tabulator-raw', 'data'),
            ddp.Output('pivot-tabulator-raw', 'columns'),
        ],
        [
            ddp.Input(f'pivot-dmi-{library}-{source}-{func}', 'n_clicks')
            for library, sources in datasets.items()
            for source, funcs in sources.items()
            for func in funcs
        ],
    )
    def load_raw_data(*n_clicks:tp.List[str]) -> tp.List[dict]:
        trigger = dash.callback_context.triggered[0]
        if not trigger['value']:
            raise dex.PreventUpdate
        
        comp = trigger['prop_id'].rsplit('.', maxsplit=1)[0]
        *_, library, source, func = comp.split('-')

        if library=='plotly':
            data = getattr(ptd, func)()
        elif library=='sklearn':
            output = getattr(skd, func)()
            if isinstance(output, sku.Bunch):
                
                Xdat = output.data
                if len(Xdat.shape)==1:
                    Xdat = Xdat[:, np.newaxis]

                Xcol = output.get('feature_names', range(Xdat.shape[1]))

                X = dict(zip(Xcol, Xdat.T))
            data = pd.DataFrame(X)
        else:
            data = pd.DataFrame()

        records = data.to_dict(orient='records')
        columns = [
            {
                'title':col,
                'field':col,
                'hozAlign':'center',
            }
            for col in data.columns
        ]
        return records, columns

    @app.callback(
        ddp.Output('pivot-div-agg', 'children'),
        [ddp.Input('pivot-tabulator-raw', 'data')],
    )
    def load_agg_data(records:tp.List[dict]) -> dpv.PivotTable:
        n = sum(len(col) for col in records[0])
        return dpv.PivotTable(id=str(pd.Timestamp.now()), data=records, unusedOrientationCutoff=n+1)