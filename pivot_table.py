# Nicholas Eterovic 2021Q3
####################################################################################################

# Dash packages.
import dash
from dash import dcc
from dash import html as dhc
import dash_tabulator as dtb
import dash.exceptions as dex
import dash_pivottable as dpv
import dash.dependencies as ddp
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
    "sklearn":{
        source:[func for func in dir(skd) if func.startswith(source)]
        for source in ["load", "fetch", "make"]
    },
    "plotly":{
        "load":[func for func in dir(ptd) if not func.startswith("_")],
    },
}

app_layout = [
    dbc.Card([
        dbc.CardBody([
            dcc.Markdown(f"""
                # The Powerful Pivot Table
                ***

                ### Introduction
                ***

                  This project is simple: combine the data aggregation of the pivot table
                with interactive data visualization.
            """),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dcc.Markdown("""
                ### The Raw Data
            """),
        ]),
        dbc.CardBody([
            dbc.InputGroup(
                size="sm",
                children=[
                    dbc.DropdownMenu(
                        label="Import",
                        size="sm",
                        color="dark",
                        menu_variant="dark",
                        direction="right",
                        addon_type="prepend",
                        children=[
                            dbc.DropdownMenuItem(
                                children="Upload",
                                n_clicks=0,
                                disabled=True,
                            ),
                        ] + [
                            dhc.Div([
                                dbc.DropdownMenu(
                                    label=library.capitalize(),
                                    size="sm",
                                    color="dark",
                                    menu_variant="dark",
                                    direction="right",
                                    disabled=(library=="sklearn"),
                                    children=[
                                        dbc.DropdownMenu(
                                            label=source.capitalize(),
                                            size="sm",
                                            color="dark",
                                            menu_variant="dark",
                                            direction="right",
                                            children=[
                                                dbc.DropdownMenuItem(
                                                    id=f"dmi-pivot-{library}-{source}-{func}",
                                                    children=func.split("_", maxsplit=1)[-1],
                                                    disabled=(source=="fetch"),
                                                    n_clicks=0,
                                                )
                                                for func in funcs
                                            ],
                                        )
                                        for source, funcs in sources.items()
                                    ],
                                )
                            ])
                            for library, sources in datasets.items()
                        ],
                    ),
                    dbc.Input(
                        type="text",
                        disabled=True,
                    ),
                ],
            ),
            dtb.DashTabulator(
                id="tabulator-pivot-raw",
                data=[],
                columns=[{
                    "title":"",
                    "field":"none",
                    "hozAlign":"center",
                    "headerSort":False,
                }],
                options={
                    "placeholder":"None",
                    "layout":"fitDataStretch",
                    "layoutColumnsOnNewData":False,
                    "minHeight":"50vh",
                    "maxHeight":"50vh",
                    "height":"50vh",
                    "pagination":"local",
                    "selectable":False,
                },
            ),
        ]),
    ]),
    dbc.Card([
        dbc.CardHeader([
            dcc.Markdown("""
                ### The Pivot Table
            """),
        ]),
        dbc.CardBody([
            dhc.Div(id="div-pivot-agg", children=[]),
        ]),
    ])
]

####################################################################################################
# CALLBACKS

def register_app_callbacks(app:dash.Dash) -> None:

    # Load default data on first tab visit.
    library, source, func = [
        (library, source, func)
        for library, sources in datasets.items()
        for source, funcs in sources.items()
        for func in funcs
    ][0]
    @app.callback(
        ddp.Output(f"dmi-pivot-{library}-{source}-{func}", "n_clicks"),
        [ddp.Input("tabs-projects", "value")],
        [ddp.State(f"dmi-pivot-{library}-{source}-{func}", "n_clicks")],
    )
    def click(tab:str, n_clicks:int) -> int:
        if tab!="pivot" or n_clicks>0:
            raise dex.PreventUpdate
        return n_clicks+1

    @app.callback(
        [
            ddp.Output("tabulator-pivot-raw", "data"),
            ddp.Output("tabulator-pivot-raw", "columns"),
        ],
        [
            ddp.Input(f"dmi-pivot-{library}-{source}-{func}", "n_clicks")
            for library, sources in datasets.items()
            for source, funcs in sources.items()
            for func in funcs
        ],
    )
    def load_raw_data(*n_clicks:tp.List[str]) -> tp.List[dict]:
        trigger = dash.callback_context.triggered[0]
        if not trigger["value"]:
            raise dex.PreventUpdate
        
        comp = trigger["prop_id"].rsplit(".", maxsplit=1)[0]
        *_, library, source, func = comp.split("-")

        if library=="plotly":
            data = getattr(ptd, func)()
        elif library=="sklearn":
            output = getattr(skd, func)()
            if isinstance(output, sku.Bunch):
                
                Xdat = output.data
                if len(Xdat.shape)==1:
                    Xdat = Xdat[:, np.newaxis]

                Xcol = output.get("feature_names", range(Xdat.shape[1]))

                X = dict(zip(Xcol, Xdat.T))
            data = pd.DataFrame(X)
        else:
            data = pd.DataFrame()

        records = data.to_dict(orient="records")
        columns = [
            {
                "title":col,
                "field":col,
                "hozAlign":"center",
            }
            for col in data.columns
        ]
        return records, columns

    @app.callback(
        ddp.Output("div-pivot-agg", "children"),
        [ddp.Input("tabulator-pivot-raw", "data")],
    )
    def load_agg_data(records:tp.List[dict]) -> dpv.PivotTable:
        n = sum(len(col) for col in records[0])
        return dpv.PivotTable(
            id=str(pd.Timestamp.now()),
            data=records,
            unusedOrientationCutoff=n+1,
        )