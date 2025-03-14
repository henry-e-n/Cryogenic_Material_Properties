import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import ALL
import pandas as pd
import numpy as np
import json
import base64
import sys, os, csv, json


from stage_calc import calculate_power_function, get_all_powers


abspath = os.path.abspath(__file__)
file_path = os.path.dirname(abspath)
sys.path.insert(0, f"{file_path}{os.sep}..{os.sep}..{os.sep}")

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

path_to_tcFiles = f"{file_path}{os.sep}..{os.sep}..{os.sep}"
all_files = os.listdir(path_to_tcFiles)
exist_files = [file for file in all_files if file.startswith("tc_fullrepo")]
tc_file_date = exist_files[0][-12:-4]

TCdata = np.loadtxt(f"{path_to_tcFiles}{os.sep}tc_fullrepo_{tc_file_date}.csv", dtype=str, delimiter=',') # imports compilation file csv


mat_list = list(TCdata[1:, 0])

# Cryogenic stages
stages = ["PTC 1", "PTC 2", "4K - LHe", "1K", "300mK", "100mK"]
stage_temps = [260, 240, 169, 4.2, 2, 0.3, 0.1]

stage_details = {}
for i in range(len(stages)):
    stage_details[stages[i]] = {"lowT": float(stage_temps[i+1]), "highT": float(stage_temps[i])}

temperature_data = [
    {"Stage": stage, 
     "Temperature (K)": stage_details[stage]["lowT"],
     "Total Power (W)": 0
    } for stage in stage_details
]

temperature_table = dash_table.DataTable(
    id='temperature-table',
    columns=[
        {"name": "Stage", "id": "Stage"},
        {"name": "Temperature (K)", "id": "Temperature (K)"},
        {"name": "Total Power (W)", "id": "Total Power (W)"}
    ],
    data=temperature_data,
    editable=False,  # Set to False if you don't want this table to be editable
    style_table={'width': '100%', 'overflowX': 'auto'},
    style_cell={'textAlign': 'center'},
)

cooling_data = [
    {
        "Headers" : "Header",
        "Values" : "Value"
    }
]

cooling_table = dash_table.DataTable(
    id='cooling-table',
    columns=[
        {"name": "Headers", "id": "Headers"},
        {"name": "Values", "id": "Values"}
    ],
    data=cooling_data,
    editable=False,  # Set to False if you don't want this table to be editable
    style_table={'width': '100%', 'overflowX': 'auto'},
    style_cell={'textAlign': 'center'},
)

# Layout of the app
app.layout = html.Div([
    html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Cryogenic Development",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Thermal Model Overview",
                                    style={"margin-top": "0px"},
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
    dcc.Tabs([
        dcc.Tab(
            label = 'Configuration',
            children=[
                html.Div([ # Division of input sector
                    html.Div(
                        [
                            html.H3(
                                "Cryogenic Thermal Stage",
                                style={"text-align": "center"},
                            ),
                        ]
                    ),
                    html.Div([
                        html.H5(
                            "Input Parameters",
                            style={"text-align": "center"},
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Cryogenic Stage"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(id="cryogenic-stage",
                                                     options=[{"label": stage, "value": stage} for stage in stages])
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ],
                            className="input-division"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Type"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.RadioItems(id="type", 
                                                       options=[{"label": "Component", "value": "Component"}, 
                                                                {"label": "Coax", "value": "Coax"}, 
                                                                {"label": "A/L", "value": "A/L"}, 
                                                                {"label": "Other", "value": "Other"}], 
                                                        value="Component",
                                                        # inline=True,
                                                        labelStyle= {"margin":"1rem"}, style = {'display': 'flex'})
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ],
                            className="input-division"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Component Name"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="component", type="text")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="component-row",
                            className="input-division"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Material"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(id="material", 
                                                    options=[{"label": m, "value": m} for m in mat_list])
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="material-row",
                            className="input-division"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "OD (m):"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="od", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="od-row"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "ID (m):"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="id", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="id-row"
                        ),
                        html.Div([
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Casing Material:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(id="case-mat", options=[{"label": m, "value": m} for m in mat_list])
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ]
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Insulator Material:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(id="insulator-mat", options=[{"label": m, "value": m} for m in mat_list])
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ]
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Core Material:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.Dropdown(id="core-mat", options=[{"label": m, "value": m} for m in mat_list])
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ]
                        )],id="coax-mat-row"),
                        html.Div([
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Case OD:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="case-od", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ]
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Insulator OD:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="insulator-od", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ]
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Core OD:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="core-od", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ]
                        )], id="coax-OD-row"),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "A/L (m):"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="A_L", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="A_L-row"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Length (m):"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="length", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="length-row"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Power per Part (W):"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="power", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="power-row"
                        ),
                        html.Div( # Single Input
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Number:"
                                        ),
                                    ],
                                    style={
                                        "width": "30%",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Div(
                                    [
                                        dbc.Input(id="number", type="number")
                                    ],
                                    style={
                                        "width": "25%",
                                        "display": "inline-block",
                                        "margin-left": "10px",
                                    },
                                ),
                            ], id="number-row"
                        ),
                    ]),
                ]),
                html.Hr(),
                dbc.Row([
                        dcc.Upload(id="upload-json", children=html.Div(['Load from JSON']), 
                                style={'width': '140px', 'height': '40px', 'lineHeight': '35px', 
                                        'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 
                                        'textAlign': 'center', 'margin': '10px'}),
                        dbc.Button("Add",             id="add",                 className="addbutton mr-2"),
                        dbc.Button("Save to JSON",    id="save-json",           className="savebutton mr-2"),
                        dbc.Button("Calculate Power", id="calculate-power",     className="calcbutton mr-2"),
                        dcc.Download(id="download-json"),
                    ]),
                html.Hr(),
                dbc.Row([
                    html.H2("Components by Cryogenic Stage"),
                    html.Div(id="table-container")
                ]),
                dbc.Row(dbc.Col(dbc.Button("Clear Cache", id="clear-cache", className="clearcachebutton mr-2"))),
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            "Henry Nachman © 2024 - for the BLAST Collaboration.",
                            className="footer-text",
                            style={
                                "textAlign": "center",
                                "padding": "20px",
                                "backgroundColor": "#f8f9fa",
                                "marginTop": "20px"
                            }
                        )
                    )
                )

            ]
        ),
        dcc.Tab(
            label = 'Results',
            children=[
                html.Div(id="temperature-table", children = [temperature_table], className="results-table"),
                html.Div(id="cooling-table", children = [cooling_table], className="results-table")
            ])
    ])
    
])

# Initial empty components dictionary
components = {stage: {} for stage in stages}

@app.callback(
    Output("table-container", "children"), #, Output("stage-details-table-container", "children")
    [Input("add", "n_clicks"), Input("upload-json", "contents"), Input("calculate-power", "n_clicks"), Input({"type": "editable-table", "index": dash.ALL}, "data")],
    [State("cryogenic-stage", "value"), State("type", "value"), State("component", "value"), State("material", "value"), State("od", "value"), 
     State("id", "value"), State("length", "value"), State("power", "value"), State("number", "value"), State("case-mat", "value"), 
     State("insulator-mat", "value"), State("core-mat", "value"), State("case-od", "value"), 
     State("insulator-od", "value"), State("core-od", "value"), State("A_L", "value"), State("table-container", "children")],
    prevent_initial_call=True
)
def add_component(n_clicks, json_contents, calc_clicks, updated_data, stage, entry_type, component, 
                  material, od, id_val, length, power, number, case_mat, insulator_mat, core_mat, case_od, insulator_od, core_od, A_L, current_table):
    global components, stage_details
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'add':
        if stage and number and component:
            if stage not in components:
                components[stage] = {}
            
            # Ensure the component name is a unique key within the stage
            if component not in components[stage]:
                components[stage][component] = {}

            if entry_type == "Component": 
                components[stage][component] = {
                    "Name": component,
                    "Type": "Component",
                    "material": material,
                    "OD": od, 
                    "ID": id_val, 
                    "length": length,
                    "number": number,
                    "Power per Part (W)": 0,
                    "Power Total (W)": 0,
                }
            elif entry_type == "Coax":
                components[stage][component] = {
                    "Name": component,
                    "Type": "Coax",
                    "mat_C": case_mat,
                    "mat_I": insulator_mat,
                    "material": core_mat,
                    "OD" : case_od,
                    "OD_I": insulator_od,
                    "OD_c": core_od,
                    "length": length,
                    "number": number,
                    "Power per Part (W)": 0,
                    "Power Total (W)": 0,
                }
            elif entry_type == "A/L":
                components[stage][component] = {
                    "Name": component,
                    "Type": "A/L",
                    "material": material,
                    "A/L" : A_L,
                    "number": number,
                    "Power per Part (W)": 0,
                    "Power Total (W)": 0,
                }
            elif entry_type == "Other" and power:
                components[stage][component] = {
                    "Name": component,
                    "Type": "Other",
                    "number": number,
                    "Power per Part (W)": power,
                    "Power Total (W)": power * number,  # Direct calculation for Other type
                }
            print("\n")
            for stage in components:
                print(f"\n{stage}")
                print(f"Components after addition: {components[stage].keys()}")
    elif trigger == 'upload-json' and json_contents:
        content_type, content_string = json_contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        json_data = json.loads(decoded)

        # Update the global components dictionary with the nested structure
        new_components = json_data.get("components", {})
        for stage, components_dict in new_components.items():
            if stage not in components:
                components[stage] = {}
            for component_name, details in components_dict.items():
                components[stage][component_name] = details

        # Update the global stage_details dictionary
        stage_details = json_data.get("stage_details", stage_details)

    elif trigger == 'calculate-power':
        components = get_all_powers(components, stage_details)
    elif trigger == "new-process-button":
        components, stage_details = optimize_tm(components, stage_details)
    elif trigger == '{"type":"editable-table","index":ALL}':
        for stage, comps in components.items():
            updated_stage_data = next(item for item in updated_data if item['index'] == stage)
            df = pd.DataFrame(updated_stage_data['data'])
            df.set_index("Name", inplace=True)
            components[stage] = df.to_dict(orient="index")

    # print("\n")
    # for stage in components:
    #     print(f"\n{stage}")
    #     print(f"Components after addition: {components[stage]}")
    # make_results()
    return generate_table()

@app.callback(
    Output("download-json", "data"),
    Input("save-json", "n_clicks"),
    prevent_initial_call=True
)
# def save_to_json(n_clicks):
#     return dict(content=json.dumps(components, indent=4), filename="components.json")
def save_to_json(n_clicks):
    # Include stage details and total power in the JSON data
    output_data = {
        "components": components,
        "stage_details": stage_details,
        "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
    }
    return dict(content=json.dumps(output_data, indent=4), filename="components.json")


@app.callback(
    [Output("component-row", "style"), Output("material-row", "style"), Output("od-row", "style"), Output("id-row", "style"), Output("length-row", "style"), 
     Output("power-row", "style"), Output("coax-mat-row", "style"), Output("coax-OD-row", "style"), Output("A_L-row", "style")],
    Input("type", "value")
)
def toggle_fields(entry_type):
    if entry_type == "Component":
        return {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}
    elif entry_type == "A/L":
        return {"display": "block"}, {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "block"}
    elif entry_type == "Coax":
        return {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "block"}, {"display": "block"}, {"display": "none"}
    elif entry_type == "Other":
        return {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}
    return {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}

@app.callback(
    Output("table-container", "children", allow_duplicate=True),
    Input({"type": "editable-table", "index": dash.ALL}, "data"),
    prevent_initial_call=True
)
def update_table_data(data):
    global components

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # print("\n UPDATE TABLE DATA")
    # for stage in components:
    #     print(f"\n{stage}")
    #     print(f"Components after addition: {components[stage].keys()}")

    for item in ctx.inputs_list[0]:
        stage = item["id"]["index"]
        updated_data = pd.DataFrame(item["value"]).set_index("Name").to_dict(orient="index")
        
        # Debug print
        # print(f"\nUpdated data for stage {stage}: {updated_data}")

        # Convert columns to appropriate data types
        for comp, details in updated_data.items():
            for key, value in details.items():
                if key in ["OD", "ID", "length", "number", "Power per Part (W)", "Power Total (W)"]:
                    try:
                        updated_data[comp][key] = float(value)
                    except ValueError:
                        updated_data[comp][key] = 0.0

        # Debug print
        # print(f"\nUpdated data after type conversion for stage {stage}: {updated_data}")

        # Merge with existing data to prevent overwriting other categories
        if stage in components:
            components[stage].update(updated_data)
        else:
            components[stage] = updated_data

    # print("\n UPDATE TABLE DATA -- 2")
    # for stage in components:
    #     print(f"\n{stage}")
    #     print(f"Components after addition: {components[stage]}")

    return generate_table()




def generate_table():
    global components
    tables = []
    # print("\n GENERATE TABLE")
    # for stage in components:
    #     print(f"\n{stage}")
    #     print(f"Components after addition: {components[stage]}")

    for stage, comps in components.items():
        if comps:
            stage_total_power = sum(details["Power Total (W)"] for details in comps.values())
            tables.append(html.H3(f"{stage} - High Temp: {stage_details[stage]['highT']:.2e} K, Low Temp: {stage_details[stage]['lowT']:.2e} K",
                                  style={
                                      "color": "#1e3799",
                                      "fontSize": "24px",
                                      "marginTop": "20px",
                                      "fontWeight": "bold",
                                      "textAlign": "center",
                                      "backgroundColor": "#AEC6CF",
                                      "padding": "8px",
                                      "borderRadius": "5px"
                                  }))
            tables.append(html.H4(f"Total Power: {stage_total_power:.2e} W",
                                  style={"color": "#1e3799", "fontSize": "20px", "textAlign": "left"}))

            entry_types = {'Component': [], 'Coax': [], 'A/L': [], 'Other': []}

            for comp, details in comps.items():
                entry_type = details.get("Type", "Component")
                entry_types[entry_type].append({"Name": comp, **details})

            # print(entry_types)
            for entry_type, items in entry_types.items():
                if items:
                    # Convert items to a DataFrame ensuring that index is reset and component names are included
                    df = pd.DataFrame(items)

                    # Ensure "Name" is the first column
                    columns = ["Name"] + [col for col in df.columns if col != "Name"]

                    total_power = df["Power Total (W)"].sum()
                    tables.append(html.H4(f"{entry_type} Components (Total Power: {total_power:.2e} W)",
                                          style={"color": "#1e3799", "fontSize": "20px", "textAlign": "left"}))
                    tables.append(dash_table.DataTable(
                        id={"type": "editable-table", "index": stage},
                        columns=[{"name": col, "id": col, "editable": True} for col in columns],
                        data=df.to_dict('records'),
                        editable=True
                    ))
        
    # print("\n GENERATE TABLE -- 2")
    # for stage in components:
    #     print(f"\n{stage}")
    #     print(f"Components after addition: {components[stage]}")

    return tables


@app.callback(
    Output("table-container", "children", allow_duplicate=True),
    [Input("clear-cache", "n_clicks")],
    prevent_initial_call=True
)
def clear_cache(n_clicks):
    global components, stage_details

    if n_clicks:
        # Reset global state variables
        components = {stage: {} for stage in stages}
        stage_details = {stage: {"lowT": lowT, "highT": highT} for stage, (lowT, highT) in stage_details.items()}

        # Return an empty table or a placeholder
        return generate_table()  # This will re-render the table with empty data

    raise dash.exceptions.PreventUpdate


@app.callback(
    [Output('temperature-table', 'data'), Output('cooling-table', 'data')],
    [Input('add', 'n_clicks'),
     Input("calculate-power", "n_clicks"),
     Input('clear-cache', 'n_clicks')],
    prevent_initial_call=True
)
def update_temperature_table(n_clicks_add, n_clicks_calc, n_clicks_clear):
    # Re-generate the temperature data based on the current state of stage_details
    updated_temperature_data = [
        {"Stage": stage, 
        "Temperature (K)": stage_details[stage]["lowT"],
        "Total Power (W)": f"{sum(components[stage][comp]['Power Total (W)'] for comp in components[stage]):.2e}"
        }
        for stage in stage_details
    ]

    # output_data = {
    #     "components": components,
    #     "stage_details": stage_details,
    #     "total_power": {stage: sum(details["Power Total (W)"] for details in comps.values()) for stage, comps in components.items()}
    # }
    # sum_var, updated_cooling_data = get_sum_variance(output_data)
    
    updated_cooling_data = [
        {
            "Headers" : 0,
            "Values" : 0
        }
    ]

    print(updated_cooling_data)

    return updated_temperature_data, updated_cooling_data


if __name__ == "__main__":
    app.run_server(debug=True)