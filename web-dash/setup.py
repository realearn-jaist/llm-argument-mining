from dash import Dash, html, dcc, dash_table
from dash.dependencies import Output, Input
import random
import dash_cytoscape as cyto
import pandas as pd
import os

cyto.load_extra_layouts()

#read CSV file
#replacing path with CSV path in your own computer
mvp1_path = "mvp1data.csv"
mvp2_path = "mvp2data.csv"
df_mvp1 = pd.read_csv(mvp1_path)
df_mvp2 = pd.read_csv(mvp2_path)

#Globle Sentences dictionary
combined_globle_list = [x for n in (df_mvp1["sentence_1"],df_mvp1["sentence_2"]) for x in n]
unique_list = list(set(combined_globle_list))
element_to_integer = {element: str(index + 1) for index, element in enumerate(unique_list)}
g_description = {value: key for key, value in element_to_integer.items()}

#Extracting sentences in each topics
unique_topics = df_mvp1['topic'].unique()
unique_topics_2 = df_mvp2['topic'].unique()
output_data = {}
output_data2 = {}

# Loop through unique topics and filter the DataFrame for each topic
for topic in unique_topics:
    filtered_df_mvp1 = df_mvp1[df_mvp1['topic'] == topic]
    output_data[f"data_{topic}"] = filtered_df_mvp1.to_dict(orient='list')
# Loop through unique topics and filter the DataFrame for each topic
for topic in unique_topics_2:
    filtered_df_mvp2 = df_mvp2[df_mvp2['topic'] == topic]
    output_data2[f"data_{topic}"] = filtered_df_mvp2.to_dict(orient='list')

# Function to finding description from Globle Sentences dictionary
def find_key_by_value(list_a, list_b):
    list_a_id, list_b_id = [], []
    for i in list_a:
        for key, value in g_description.items():
            if value == i:
                list_a_id.append(key)
    for i in list_b:
        for key, value in g_description.items():
            if value == i:
                list_b_id.append(key)
    return list_a_id, list_b_id

# Function Create nodes and edges for creating graph
def create_elements(sen1, sen2, relation, attack, nonattack, nodeinfo):
    elements = []
    # Nodes
    combined_list = [x for n in (sen1, sen2) for x in n]
    for i in combined_list:
        elements.append({
                'data': {'id': str(i), 'label': str(i)}
            })

    # Edges with different classes based on 'relation'
    for i in range(len(sen1)):
        if relation[i] == 1:
            rela = "Attack"
        elif relation[i] == 2:
            rela = "Non-Attack (Support)"
        else:
            rela = "Non-Attack (Neither)"
        edge_data = {
            'data': {
                'source': str(sen1[i]),
                'target': str(sen2[i]),
                'label': str(sen1[i]) + " " + rela + " " + str(sen2[i]),
            }
        }

        if relation[i] == 1:
            edge_data['classes'] = 'red'
        elif relation[i] == 2:
            edge_data['classes'] = 'green'
        else:
            edge_data['classes'] = 'green'  # Default class if 'relation' value is not 1 or 2

        if attack and relation[i] == 1:
            elements.append(edge_data)
        elif nonattack and relation[i] != 1:
            elements.append(edge_data)

    return elements

def create_Acc_elements(sen1, sen2, relation, attack, nonattack, nodeinfo, satis):
    elements = []
    # Nodes
    combined_list = [x for n in (sen1, sen2) for x in n]
    for i in combined_list:
        elements.append({
                'data': {'id': str(i), 'label': str(i)}
            })

    # Edges with different classes based on 'relation'
    for i in range(len(sen1)):
        if satis[i]==1:
            if relation[i] == 1:
                rela = "Attack"
            elif relation[i] == 2:
                rela = "Non-Attack (Support)"
            else:
                rela = "Non-Attack (Neither)"
            edge_data = {
                'data': {
                    'source': str(sen1[i]),
                    'target': str(sen2[i]),
                    'label': str(sen1[i]) + " " + rela + " " + str(sen2[i]),
                }
            }

            if relation[i] == 1:
                edge_data['classes'] = 'red'
            elif relation[i] == 2:
                edge_data['classes'] = 'green'
            else:
                edge_data['classes'] = 'green'  # Default class if 'relation' value is not 1 or 2

            if attack and relation[i] == 1:
                elements.append(edge_data)
            elif nonattack and relation[i] != 1:
                elements.append(edge_data)

    return elements


#Styles Sheet
styles = {
    'container_style': {
        'position': 'fixed',
        'display': 'flex',
        'flex-direction': 'column',
        'height': '100vh',  # Full height
        'width': '100%',   # Full width
        'background': 'linear-gradient(180deg, #ffffff 0%, #e0e0e0 100%)',  # Background gradient
    },
    'cytoscape': {
        'position': 'absolute',
        'width': '100%',
        'height': '450px',
        'z-index': 999,
    },
    'dropdown_style': {
        'margin': '0 auto',
        'text-align': 'center',
        'max-width': '500px',
    },
    'graph_container': {
        'max-width': '2000px',
        'margin': '0px auto',
        'display': 'grid',
        'grid-template-columns': 'repeat(2, 1fr)',
        'grid-gap': '20px',
        'padding': '50px',
        'background-color': '#fff',
        'box-shadow': '0 0 10px rgba(0, 0, 0, 0.1)',# Space between graph containers
    },
    'container': {
        'max-width': '2000px',
        'margin': '0px auto',
        'display': 'flex',
        'justify-content': 'space-between',
        'padding': '50px',
        'background-color': '#fff',
        'box-shadow': '0 0 10px rgba(0, 0, 0, 0.1)',
    },
    'container-colmn': {
        'display': 'flex',
        'fex-flow' : 'column wrap'
    },
    'left-column': {
        'text-align': 'center',
        'flex': '1',
        'padding':' 10px',
        'background-color': '#f9f9f9',
    },

    'right-column': {
        'text-align': 'center',
        'flex': '1',
        'padding': '10px',
        'background-color': '#f0f0f0',
    },
}



app = Dash(__name__)

server = app.server

app.layout = html.Div([
    html.Div(children=[
        html.Div(style=styles['container'],children=[
            html.Div(style=styles['left-column'], children=[
                html.P("Choose Topic:"),
                dcc.Dropdown(
                    id='Topic_selection',
                    value='Data_election',
                    clearable=False,
                    options=[
                        {'label': topic.capitalize(), 'value': topic}
                        for topic in output_data
                    ],
                    style=styles['dropdown_style'],
                )]),
            html.Div(style=styles['right-column'], children=[
                # html.Div(style=styles['container'], children=[
                    html.Div(children=[
                        html.P("Graph-Type:"),
                        dcc.Dropdown(
                            id='dpdn',
                            value='circle',
                            clearable=False,
                            options=[
                                {'label': name.capitalize(), 'value': name}
                                for name in ['cose', 'breadthfirst', 'grid', 'random', 'circle', 'concentric']
                            ],
                            style=styles['dropdown_style'],
                        ),
                    ]),
                    html.Div(children=[
                        dcc.Checklist(
                            ['Node information'],
                            [],
                            id = 'infocheck',
                            inline=True
                        ),
                        dcc.Checklist(
                            ['Attack', 'Non-Attack'],
                            ['Attack', 'Non-Attack'],
                            id='atkcheck',
                            inline=True
                        ),
                    ]),
                # ])
            ]),
        ]),
    ]),
    html.Div(style=styles['graph_container'],children=[
        html.Div(children=[
            html.Div(style=styles['left-column'], children=[
            html.P("Relation Graph: default")]),
            cyto.Cytoscape(
                id='graph_default',
                style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
                elements=[],
                stylesheet = [],
                responsive=True,
            ),
            # html.Div(style=styles['container'],children=[
            html.Div(style=styles['left-column'], children=[
            html.P(id='default-Node-output'),]),
            html.Div(style=styles['left-column'], children=[
            html.P(id='default-Edge-output')
            ])
            # ]),
            ]),
    html.Div(children=[
            html.Div(style=styles['right-column'], children=[
            html.P("Acceptable Relation Graph: default")]),
            cyto.Cytoscape(
                id='Acc_graph_default',
                style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
                elements=[],
                stylesheet = [],
                responsive=True,
            ),
            # html.Div(style=styles['container'],children=[
            html.Div(style=styles['right-column'], children=[
            html.P(id='Acc_default-Node-output'),]),
            html.Div(style=styles['right-column'], children=[
            html.P(id='Acc_default-Edge-output')
            ])
            # ]),
            ]),
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: Text davincii")]),
        cyto.Cytoscape(
        id='graph_davincii',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='davincii-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='davincii-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: Text davincii")]),
        cyto.Cytoscape(
        id='Acc_graph_davincii',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_davincii-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_davincii-Edge-output')
        ])
        # ]),
    ]),
    
    
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: GPT 3.5")]),
        cyto.Cytoscape(
        id='graph_gpt_35',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='35-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='35-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: GPT 3.5")]),
        cyto.Cytoscape(
        id='Acc_graph_gpt_35',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_35-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_35-Edge-output')
        ])
        # ]),
    ]),
    
    
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: GPT 3.5 version 0613")]),
        cyto.Cytoscape(
        id='graph_gpt_35_0613',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='0613-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='0613-Edge-output')
        ])
        # ]),
    ]),
    
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: GPT 3.5 version 0613")]),
        cyto.Cytoscape(
        id='Acc_graph_gpt_35_0613',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_0613-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_0613-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: Support Vector Machines")]),
        cyto.Cytoscape(
        id='graph_SVM',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='SVM-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='SVM-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: Support Vector Machines")]),
        cyto.Cytoscape(
        id='Acc_graph_SVM',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_SVM-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_SVM-Edge-output')
        ])
        # ]),
    ]),
    
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: Decision Tree")]),
        cyto.Cytoscape(
        id='graph_Tree',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='Tree-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='Tree-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: Decision Tree")]),
        cyto.Cytoscape(
        id='Acc_graph_Tree',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_Tree-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_Tree-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: Naive Bayes")]),
        cyto.Cytoscape(
        id='graph_NB',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='NB-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='NB-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: Naive Bayes")]),
        cyto.Cytoscape(
        id='Acc_graph_NB',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_NB-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_NB-Edge-output')
        ])
        # ]),
    ]),
    
    html.Div(children=[
        html.Div(style=styles['left-column'], children=[
        html.P("Relation Graph: Logistic Regression")]),
        cyto.Cytoscape(
        id='graph_LR',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['left-column'], children=[
        html.P(id='LR-Node-output'),]),
        html.Div(style=styles['left-column'], children=[
        html.P(id='LR-Edge-output')
        ])
        # ]),
    ]),
    html.Div(children=[
        html.Div(style=styles['right-column'], children=[
        html.P("Acceptable Relation Graph: Logistic Regression")]),
        cyto.Cytoscape(
        id='Acc_graph_LR',
        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'},
        elements=[],
        stylesheet = [],
        responsive=True,
        ),
        # html.Div(style=styles['container'],children=[
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_LR-Node-output'),]),
        html.Div(style=styles['right-column'], children=[
        html.P(id='Acc_LR-Edge-output')
        ])
        # ]),
    ]),]),
    html.Div(children=[
        html.Div(style=styles['container'],children=[
            html.Div(style=styles['left-column'], children=[
            html.P(id="Nodes_Description-left"),
            ]),
            html.Div(style=styles['right-column'], children=[
            html.P(id="Nodes_Description-right"),
            ]),
    ]),
    ])
])

#Call back Function to display node's description in each topic
@app.callback(Output('Nodes_Description-left', 'children'),Output('Nodes_Description-right', 'children'), Input('Topic_selection', 'value'))
def displayDescriptionNodeData(data):
    if data != '':
        if data in output_data:
            sen1 = output_data[data]['sentence_1']
            sen2 = output_data[data]['sentence_2']

            description = []
            check_dup = []
            for i in range(len(sen1)):
                node1, node2 = [], []
                for key, value in g_description.items():
                    if sen1[i] == value and sen1[i] not in check_dup:
                        node1.append(key)
                        node1.append(value)
                        description.append(node1)
                        check_dup.append(value)
                    if sen2[i] == value and sen2[i] not in check_dup:
                        node2.append(key)
                        node2.append(value)
                        description.append(node2)
                        check_dup.append(value)
                        
            # Sort the description list based on the "Key"
            description.sort(key=lambda x: x[0].lower())
            
            # Split the description list into two halves
            midpoint = len(description) // 2
            first_half = description[:midpoint]
            second_half = description[midpoint:]

            table_style = {'textAlign': 'left', 'margin-bottom': '10px'}  # Adjust the values as needed

            # Set the desired fixed length for each cell
            cell_length = 250

            table_1 = dash_table.DataTable(
                id='table-left',
                columns=[
                    {'name': 'Key', 'id': 'Key'},
                    {'name': 'Value', 'id': 'Value'},
                ],
                data=[
                    {'Key': key, 'Value': value} for key, value in first_half
                ],
                style_table=table_style,
                style_cell={'textAlign': 'left', 'minWidth': 0, 'maxWidth': cell_length, 'whiteSpace': 'normal'},
            )

            table_2 = dash_table.DataTable(
                id='table-right',
                columns=[
                    {'name': 'Key', 'id': 'Key'},
                    {'name': 'Value', 'id': 'Value'},
                ],
                data=[
                    {'Key': key, 'Value': value} for key, value in second_half
                ],
                style_table=table_style,
                style_cell={'textAlign': 'left', 'minWidth': 0, 'maxWidth': cell_length, 'whiteSpace': 'normal'},
            )

            return table_1, table_2
        else:
            return "Nodes Description Section", "Select topic first"

#Call back Function to updating topic
@app.callback(
    Output('graph_default', 'elements'),
    Output('graph_davincii', 'elements'),
    Output('graph_gpt_35', 'elements'),
    Output('graph_gpt_35_0613', 'elements'),
    Output('graph_default', 'stylesheet'),
    Output('graph_davincii', 'stylesheet'),
    Output('graph_gpt_35', 'stylesheet'),
    Output('graph_gpt_35_0613', 'stylesheet'),
    Output('graph_SVM', 'elements'),
    Output('graph_Tree', 'elements'),
    Output('graph_NB', 'elements'),
    Output('graph_LR', 'elements'),
    Output('graph_SVM', 'stylesheet'),
    Output('graph_Tree', 'stylesheet'),
    Output('graph_NB', 'stylesheet'),
    Output('graph_LR', 'stylesheet'),
    Input('Topic_selection', 'value'),
    Input('atkcheck', 'value'),
    Input('infocheck', 'value'))
def update_topic(topic_value, checklist_value, infocheck_value):
    attack = 'Attack' in checklist_value
    nonattack = 'Non-Attack' in checklist_value
    show_node_label = 'Node information' in infocheck_value

    if topic_value in output_data:
        sen1 = output_data[topic_value]['sentence_1']
        sen2 = output_data[topic_value]['sentence_2']
        sen1, sen2 = find_key_by_value(sen1, sen2)
        
        sen21 = output_data2[topic_value]['sentence_1']
        sen22 = output_data2[topic_value]['sentence_2']
        sen21, sen22 = find_key_by_value(sen21, sen22)
        
        def_element = create_elements(sen21, sen22, output_data2[topic_value]['relation_BAF'], attack, nonattack, show_node_label)
        devin_element = create_elements(sen21, sen22, output_data2[topic_value]['gpt_davinci'], attack, nonattack, show_node_label)
        gpt35_element = create_elements(sen21, sen22, output_data2[topic_value]['gpt_35'], attack, nonattack, show_node_label)
        gpt350613_element = create_elements(sen21, sen22, output_data2[topic_value]['gpt_35_0613'], attack, nonattack, show_node_label)
        SVM_element = create_elements(sen21, sen22, output_data2[topic_value]['SVM'], attack, nonattack, show_node_label)
        Tree_element = create_elements(sen21, sen22, output_data2[topic_value]['Decision_Tree'], attack, nonattack, show_node_label)
        NB_element = create_elements(sen21, sen22, output_data2[topic_value]['Naive_Bayes'], attack, nonattack, show_node_label)
        LR_element = create_elements(sen21, sen22, output_data2[topic_value]['LR'], attack, nonattack, show_node_label)
        # Use a default stylesheet or define a custom one based on your requirements
        default_stylesheet = [{
            'selector': 'node',
            'style': {'content': 'data(label)'}
        },
        {
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }},{
            'selector': '.green',
            'style': {
                'background-color': 'green',
                'line-color': 'green'
        }},{
            'selector': '.blue',
            'style': {
                'background-color': 'blue',
                'line-color': 'blue'
            }
        }]

        # Update the stylesheet based on the show_node_label condition
        stylesheet = default_stylesheet if show_node_label else [{
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }},{
            'selector': '.green',
            'style': {
                'background-color': 'green',
                'line-color': 'green'
        }},{
            'selector': '.blue',
            'style': {
                'background-color': 'blue',
                'line-color': 'blue'
            }
        }]

        return def_element, devin_element, gpt35_element, gpt350613_element, stylesheet, stylesheet, stylesheet, stylesheet, SVM_element, Tree_element, NB_element, LR_element, stylesheet, stylesheet, stylesheet, stylesheet

    return [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

#Call back Function to updating topic
@app.callback(
    Output('Acc_graph_default', 'elements'),
    Output('Acc_graph_davincii', 'elements'),
    Output('Acc_graph_gpt_35', 'elements'),
    Output('Acc_graph_gpt_35_0613', 'elements'),
    Output('Acc_graph_SVM', 'elements'),
    Output('Acc_graph_Tree', 'elements'),
    Output('Acc_graph_NB', 'elements'),
    Output('Acc_graph_LR', 'elements'),
    Output('Acc_graph_default', 'stylesheet'),
    Output('Acc_graph_davincii', 'stylesheet'),
    Output('Acc_graph_gpt_35', 'stylesheet'),
    Output('Acc_graph_gpt_35_0613', 'stylesheet'),
    Output('Acc_graph_SVM', 'stylesheet'),
    Output('Acc_graph_Tree', 'stylesheet'),
    Output('Acc_graph_NB', 'stylesheet'),
    Output('Acc_graph_LR', 'stylesheet'),
    Input('Topic_selection', 'value'),
    Input('atkcheck', 'value'),
    Input('infocheck', 'value'))
def update_acc_topic(topic_value, checklist_value, infocheck_value):
    attack = 'Attack' in checklist_value
    nonattack = 'Non-Attack' in checklist_value
    show_node_label = 'Node information' in infocheck_value

    if topic_value in output_data2:
        sen1 = output_data2[topic_value]['sentence_1']
        sen2 = output_data2[topic_value]['sentence_2']
        sen1, sen2 = find_key_by_value(sen1, sen2)
        def_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['relation_AAF'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_relation_AAF'])
        devin_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['gpt_davinci'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_gpt_davinci'])
        gpt35_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['gpt_35'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_gpt_35'])
        gpt350613_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['gpt_35_0613'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_gpt_35_0613'])
        
        SVM_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['SVM'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_SVM'])
        Tree_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['Decision_Tree'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_Decision_Tree'])
        NB_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['Naive_Bayes'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_Naive_Bayes'])
        LR_element = create_Acc_elements(sen1, sen2, output_data2[topic_value]['LR'], attack, nonattack, show_node_label,output_data2[topic_value]['satis_LR'])
        # Use a default stylesheet or define a custom one based on your requirements
        default_stylesheet = [{
            'selector': 'node',
            'style': {'content': 'data(label)'}
        },
        {
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }},{
            'selector': '.green',
            'style': {
                'background-color': 'green',
                'line-color': 'green'
        }},{
            'selector': '.blue',
            'style': {
                'background-color': 'blue',
                'line-color': 'blue'
            }
        }]

        # Update the stylesheet based on the show_node_label condition
        stylesheet = default_stylesheet if show_node_label else [{
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }},{
            'selector': '.green',
            'style': {
                'background-color': 'green',
                'line-color': 'green'
        }},{
            'selector': '.blue',
            'style': {
                'background-color': 'blue',
                'line-color': 'blue'
            }
        }]

        return def_element, devin_element, gpt35_element, gpt350613_element, SVM_element, Tree_element, NB_element, LR_element, stylesheet, stylesheet, stylesheet, stylesheet, stylesheet, stylesheet, stylesheet, stylesheet

    return [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []


#Call back Function to display node's sentences
@app.callback(Output('default-Node-output', 'children'), Input('graph_default', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node to see its meaning"
#Call back Function to display edge's relation
@app.callback(Output('default-Edge-output', 'children'),Input('graph_default', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('Acc_default-Node-output', 'children'), Input('Acc_graph_default', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node to see its meaning"
#Call back Function to display edge's relation
@app.callback(Output('Acc_default-Edge-output', 'children'),Input('Acc_graph_default', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('davincii-Node-output', 'children'), Input('graph_davincii', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node to see its meaning"
#Call back Function to display edge's relation
@app.callback(Output('davincii-Edge-output', 'children'),Input('graph_davincii', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('Acc_davincii-Node-output', 'children'), Input('Acc_graph_davincii', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node to see its meaning"
#Call back Function to display edge's relation
@app.callback(Output('Acc_davincii-Edge-output', 'children'),Input('Acc_graph_davincii', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('35-Node-output', 'children'), Input('graph_gpt_35', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node to see its meaning"
#Call back Function to display edge's relation
@app.callback(Output('35-Edge-output', 'children'),Input('graph_gpt_35', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('Acc_35-Node-output', 'children'), Input('Acc_graph_gpt_35', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node to see its meaning"
#Call back Function to display edge's relation
@app.callback(Output('Acc_35-Edge-output', 'children'),Input('Acc_graph_gpt_35', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('0613-Node-output', 'children'), Input('graph_gpt_35_0613', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('0613-Edge-output', 'children'),Input('graph_gpt_35_0613', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('Acc_0613-Node-output', 'children'), Input('Acc_graph_gpt_35_0613', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('Acc_0613-Edge-output', 'children'),Input('Acc_graph_gpt_35_0613', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('SVM-Node-output', 'children'), Input('graph_SVM', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('SVM-Edge-output', 'children'),Input('graph_SVM', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"
    
#Call back Function to display node's sentences
@app.callback(Output('Acc_SVM-Node-output', 'children'), Input('Acc_graph_SVM', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('Acc_SVM-Edge-output', 'children'),Input('Acc_graph_SVM', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('Tree-Node-output', 'children'), Input('graph_Tree', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('Tree-Edge-output', 'children'),Input('graph_Tree', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"
    
#Call back Function to display node's sentences
@app.callback(Output('Acc_Tree-Node-output', 'children'), Input('Acc_graph_Tree', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('Acc_Tree-Edge-output', 'children'),Input('Acc_graph_Tree', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('NB-Node-output', 'children'), Input('graph_NB', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('NB-Edge-output', 'children'),Input('graph_NB', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"
    
#Call back Function to display node's sentences
@app.callback(Output('Acc_NB-Node-output', 'children'), Input('Acc_graph_NB', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('Acc_NB-Edge-output', 'children'),Input('Acc_graph_NB', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"

#Call back Function to display node's sentences
@app.callback(Output('LR-Node-output', 'children'), Input('graph_LR', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('LR-Edge-output', 'children'),Input('graph_LR', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"
    
#Call back Function to display node's sentences
@app.callback(Output('Acc_LR-Node-output', 'children'), Input('Acc_graph_LR', 'tapNodeData'))
def displayTapNodeData(data):
    if data:
        node_label = data['label']
        for key, value in g_description.items():
            if key == node_label:
                description = value
        return f"ID {node_label} is {description}"
    else:
        return "Click on node"
#Call back Function to display edge's relation
@app.callback(Output('Acc_LR-Edge-output', 'children'),Input('Acc_graph_LR', 'tapEdgeData'))
def displayTapEdgeData(data):
    if data:
        return "Argument " + data['label']
    else:
        return "Click on edge to see its meaning"


#Call back Function to change layout of graph
@app.callback(Output('graph_default', 'layout'),
              Output('graph_davincii', 'layout'),
              Output('graph_gpt_35', 'layout'),
              Output('graph_gpt_35_0613', 'layout'),
              Output('Acc_graph_default', 'layout'),
              Output('Acc_graph_davincii', 'layout'),
              Output('Acc_graph_gpt_35', 'layout'),
              Output('Acc_graph_gpt_35_0613', 'layout'),
              Output('graph_SVM', 'layout'),
              Output('graph_Tree', 'layout'),
              Output('graph_NB', 'layout'),
              Output('graph_LR', 'layout'),
              Output('Acc_graph_SVM', 'layout'),
              Output('Acc_graph_Tree', 'layout'),
              Output('Acc_graph_NB', 'layout'),
              Output('Acc_graph_LR', 'layout'),
              Input('dpdn', 'value'))
def update_layout(layout_value):
    if layout_value == 'breadthfirst':
        return {
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        }
    else:
        return {
            'name': layout_value,
            'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
            'name': layout_value,
            'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        },{
        'name': layout_value,
        'animate': True
        }


if __name__ == '__main__':
    app.run(debug=True)