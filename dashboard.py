from dash import Dash, html, dash_table, dcc, callback, Output, Input,clientside_callback
import pandas as pd
import numpy as np
import plotly.express as px
import dash_mantine_components as dmc
from ml_model import predict_cost
from dash_iconify import DashIconify
import uuid
from time import sleep

link = 'https://docs.google.com/spreadsheets/d/e/' \
       '2PACX-1vQxxmZm6YG54VucQ9yRgWFQXtOI-RFJ5-sOLT93LpaYGYc-vabL9LOzzkRXX' \
       '-LmSROTA7hOL1C327nZ/pub?gid=213261502&single=true&output=csv'
df = pd.read_csv(link)

external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)


def create_text(label):
    return dmc.Text(
        label,
        size="xl",
        color="gray",
    )
def create_select(id,label, data):
    return dmc.Select(
        id=f"select_{id}",
        label=label,
        description="Выбрать(есть поиск)",
        searchable=True,
        clearable=True,
        style={"width": 200},
        data=[{"value": item, "label": item} for item in data]
        )
def create_number_input(id, label):
    return dmc.NumberInput(
        id = f"number_{id}",
        label=label,
        description="Указать или удерживать стрелку",
        stepHoldDelay=500,
        stepHoldInterval=100,
        value=0,
        style={"width": 200}
)

# App layout
app.layout = dmc.Container([
    dmc.Header(
        height=50,
        children=[dmc.Container(
                    fluid=True,
                    style={"paddingRight": 12, "paddingLeft": 12},
                    children=dmc.Group(
                        position="apart",
                        align="flex-start",
                        children=[
                            dmc.Center(
                                dcc.Link(
                                    [
                                        dmc.MediaQuery(
                                            create_text("Research Property Market"),
                                            smallerThan="sm",
                                            styles={"display": "none"},
                                        ),
                                        dmc.MediaQuery(
                                            create_text("RPM"),
                                            largerThan="sm",
                                            styles={"display": "none"},
                                        ),
                                    ],
                                    href="/",
                                    style={"paddingTop": 3, "textDecoration": "none"},
                                ),
                            ),
                        ],
                    ),
                )
            ],
        ),
    dmc.Space(h=40),
    html.Div([
        dmc.Group(
            position="apart",
            align='initial', #flex-start
            grow =False,
            spacing ='xs',
            children=[
                        create_number_input(1,"Этаж"),
                        create_number_input(2, "Этажей в доме"),
                        create_number_input(3, "Кол-во комнат"),
                        create_number_input(4, "Общая площадь"),
                        create_number_input(5, "Год постройки"),
                        create_number_input(6, "Жилая площадь"),
                        create_number_input(7, "Площадь кухни"),
                        create_select(8,'Застройщик/Агенство', np.array(["ПИК","GloraX"])),
                        create_select(9,'Город', np.array(['Moskva','Sankt-Peterburg'])),
                        create_select(10,'Район', np.array(['Moskva','Sankt-Peterburg'])),
                        create_select(11,'Улица', np.array(['Moskva','Sankt-Peterburg'])),
                        create_select(12,'Ближайшее метро', np.array(['Moskva','Sankt-Peterburg'])),
                    ],
                ),
        dmc.Text(id="prediction", mt=20),
        html.Div(
                    [
                        dmc.Button(
                            "Узнать стоимость",
                            id="loading-button-pred",
                            leftIcon=DashIconify(icon="ph:currency-rub-fill"),
                        ),
                    ]
                )
    ]),
        dmc.Stack(
            children=[dmc.Space(h=10),dmc.Divider(variant="solid"),dmc.Space(h=10)]
            ),
            dmc.Grid([
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Container(
                                children=[dmc.RadioGroup([
                                        dmc.Radio(i, value=k) for i,k in [['Москва','Moskva'],['Санкт-Петербург',
                                                                                               'Sankt-Peterburg']]],
                                         id='my-dmc-radio-item',
                                         value='Moskva',
                                         size="sm"),
                                        dcc.Graph(figure={}, id='graph-placeholder')
                                    ]
                                )
                             ], shadow="xs", p="xs", radius="lg",withBorder = True)], span=6),
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Container(
                                children=[]
                                )
                             ], shadow="xs", p="xs", radius="lg",withBorder = True)], span=6),
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Container(
                                children=[]
                                )
                             ], shadow="xs", p="xs", radius="lg",withBorder = True)], span=6)
            ]),
    ], fluid=True)

@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='my-dmc-radio-item', component_property='value')
)
def update_graph(col_chosen):
        top10_devs = (df.query('city == @col_chosen').author.value_counts(normalize=True) * 100).to_frame().reset_index()[:10]
        x = top10_devs.author.str.slice(stop=12)
        x = x.where(x.str.len() != 12,x.str.cat(['..'] * len(top10_devs)))
        labels = {'x': 'Субъект','proportion':'% на рынке'}
        fig = px.histogram(top10_devs, x=x,y='proportion',text_auto ='.2f',labels=labels, title = 'Топ-10 '
                                                                                                  'застройщиков/агенств')
        return fig
@callback(# синтаксис колбэк-функций должен быть именно таким
    Output("loading-button-pred", "loading"),
    Output(component_id="prediction", component_property="children"),
    [Input(component_id="number_1", component_property="value"),
    Input(component_id="number_2", component_property="value"),
    Input(component_id="number_3", component_property="value"),
    Input(component_id="number_4", component_property="value"),
    Input(component_id="number_5", component_property="value"),
    Input(component_id="number_6", component_property="value"),
    Input(component_id="number_7", component_property="value"),
    Input(component_id="select_8", component_property="value"),
    Input(component_id="select_9", component_property="value"),
    Input(component_id="select_10", component_property="value"),
    Input(component_id="select_11", component_property="value"),
    Input(component_id="select_12", component_property="value")],
    Input("loading-button-pred", "n_clicks"),
    prevent_initial_call=True,
)
def new_item(floor,floors_count, rooms,
             total_meters, year, living_meters,
             kitchen_meters, author,city,
             disctrict,street,underground,n_clicks):
    sleep(2)
    return  False, f'Примерная стоимость: ...{author,city,floor}'

clientside_callback(# функция JS, будет выполнена на стороне клиента
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("loading-button-pred", "loading", allow_duplicate=True),
    Input("loading-button-pred", "n_clicks"),
    prevent_initial_call=True,
)


if __name__ == '__main__':
    app.run_server(debug=True)
