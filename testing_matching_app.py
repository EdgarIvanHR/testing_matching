import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from collections import Counter

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Función para calcular la similitud basada en bigramas
def bigram_similarity(str1, str2):
    def get_bigrams(s):
        return [s[i:i+2] for i in range(len(s)-1)]
    
    bigrams1 = Counter(get_bigrams(str1.lower()))
    bigrams2 = Counter(get_bigrams(str2.lower()))
    intersection = sum((bigrams1 & bigrams2).values())
    total = sum((bigrams1 | bigrams2).values())
    return intersection / total if total > 0 else 0

# Función de comparación detallada
def comparar_personas(data1, data2, umbrales):
    resultados = {}
    res_sim,res = {},{}
    
    nombre_completo1 = f"{data1['nombre']} {data1['apellido1_']} {data1['apellido2_']}"
    nombre_completo2 = f"{data2['nombre']} {data2['apellido1_']} {data2['apellido2_']}"
    resultados['nombre_completo'] = bigram_similarity(nombre_completo1, nombre_completo2) >= umbrales['nombre_completo']
    res_sim['nombre_completo'] = ' ---> ' + str(bigram_similarity(nombre_completo1, nombre_completo2))
    res['nombre_completo'] = bigram_similarity(nombre_completo1, nombre_completo2)
    
    for key in data1:
        if key in umbrales and data1[key] and data2[key]:
            resultados[key] = bigram_similarity(data1[key], data2[key]) >= umbrales[key]
            res_sim[key] = ' ---> ' + str(bigram_similarity(data1[key], data2[key])) 
            res[key] = bigram_similarity(data1[key], data2[key])
        else:
            resultados[key] = data1[key] == data2[key] if data1[key] and data2[key] else False
            res_sim[key]  = ' '
    
    coincidencias = sum(resultados.values())
    total_campos = len(resultados)
    # coincidencia_general = "Sí" if coincidencias == total_campos else "No"
    if res['nombre_completo'] > .85 and sum([resultados[key] for key in ['nacimiento', 'escolaridad', 'genero', 'migrante', 'grupo_etnico'] ]) >= 4:
        coincidencia_general = 'Sí'  
    elif  res['nombre_completo'] > .7 and sum([res[key] for key in ['nombre', 'apellido1_', 'apellido2_'] ]) >= 2.1 and sum([resultados[key] for key in ['nacimiento', 'escolaridad', 'genero', 'migrante', 'grupo_etnico'] ]) == 5:
        coincidencia_general = 'Sí' 
    else:
        coincidencia_general = 'No' 
    
    detalle = html.Ul([html.Li(f"{campo}: {'Coincide' if resultado else 'No coincide'}  {res_sim[campo]}") for campo, resultado in resultados.items()])
    
    return html.Div([
        html.H5(f"Coincidencias: {coincidencias} de {total_campos} campos."),
        detalle,
        html.H4(f"¿Coincidencia general? {coincidencia_general}")
    ])

# Layout de la app
app.layout = dbc.Container([
    html.H2("Comparación de Identidad"),
    
    html.H4("Individuo 1"),
    dcc.Input(id='nombre1', type='text', placeholder='Nombre'),
    dcc.Input(id='apellido1_1', type='text', placeholder='Primer Apellido'),
    dcc.Input(id='apellido1_2', type='text', placeholder='Segundo Apellido'),
    dcc.DatePickerSingle(id='nacimiento1', placeholder='Fecha de Nacimiento'),
    dcc.Dropdown(id='escolaridad1', options=[
        {'label': lvl, 'value': lvl} for lvl in ['Primaria', 'Secundaria', 'Preparatoria', 'Universidad']], placeholder='Escolaridad'),
    dcc.Dropdown(id='genero1', options=[
        {'label': g, 'value': g} for g in ['Masculino', 'Femenino', 'Otro']], placeholder='Género'),
    dcc.Dropdown(id='migrante1', options=[{'label': 'Sí', 'value': 'Sí'}, {'label': 'No', 'value': 'No'}], placeholder='Migrante'),
    dcc.Input(id='grupo_etnico1', type='text', placeholder='Grupo Étnico'),
    
    html.H4("Individuo 2"),
    dcc.Input(id='nombre2', type='text', placeholder='Nombre'),
    dcc.Input(id='apellido2_1', type='text', placeholder='Primer Apellido'),
    dcc.Input(id='apellido2_2', type='text', placeholder='Segundo Apellido'),
    dcc.DatePickerSingle(id='nacimiento2', placeholder='Fecha de Nacimiento'),
    dcc.Dropdown(id='escolaridad2', options=[
        {'label': lvl, 'value': lvl} for lvl in ['Primaria', 'Secundaria', 'Preparatoria', 'Universidad']], placeholder='Escolaridad'),
    dcc.Dropdown(id='genero2', options=[
        {'label': g, 'value': g} for g in ['Masculino', 'Femenino', 'Otro']], placeholder='Género'),
    dcc.Dropdown(id='migrante2', options=[{'label': 'Sí', 'value': 'Sí'}, {'label': 'No', 'value': 'No'}], placeholder='Migrante'),
    dcc.Input(id='grupo_etnico2', type='text', placeholder='Grupo Étnico'),
    
    html.H4("Umbrales de Similitud"),
    html.Label("Nombre"),
    dcc.Slider(id='umbral_nombre', min=0, max=1, step=0.05, value=0.6, 
               marks={i/10: str(i/10) for i in range(0, 11)}),
    html.Label("Primer Apellido"),
    dcc.Slider(id='umbral_apellido1', min=0, max=1, step=0.05, value=0.6, 
               marks={i/10: str(i/10) for i in range(0, 11)}),
    html.Label("Segundo Apellido"),
    dcc.Slider(id='umbral_apellido2', min=0, max=1, step=0.05, value=0.6, 
               marks={i/10: str(i/10) for i in range(0, 11)}),
    html.Label("Nombre Completo"),
    dcc.Slider(id='umbral_nombre_completo', min=0, max=1, step=0.05, value=0.6, 
               marks={i/10: str(i/10) for i in range(0, 11)}),
    
    html.Br(),
    dbc.Button("Comparar", id='boton', color='primary'),
    html.Br(), html.Br(),
    html.Div(id='resultado')
])


@app.callback(
    Output('resultado', 'children'),
    Input('boton', 'n_clicks'),
    [State(f'{campo}{i}', 'value') if 'nacimiento' not in campo else State(f'{campo}{i}', 'date') 
     for i in [1, 2] for campo in ['nombre', 'apellido1_', 'apellido2_', 'nacimiento', 'escolaridad', 'genero', 'migrante', 'grupo_etnico']]
    + [State('umbral_nombre', 'value'), State('umbral_apellido1', 'value'), State('umbral_apellido2', 'value'), State('umbral_nombre_completo', 'value')]
)
def procesar(n_clicks, *valores):
    if not n_clicks:
        return ""
    umbrales = dict(zip(['nombre', 'apellido1_', 'apellido2_', 'nombre_completo'], valores[-4:]))
    data1 = {k: valores[i] for i, k in enumerate(['nombre', 'apellido1_', 'apellido2_', 'nacimiento', 'escolaridad', 'genero', 'migrante', 'grupo_etnico'])}
    data2 = {k: valores[i + 8] for i, k in enumerate(['nombre', 'apellido1_', 'apellido2_',  'nacimiento', 'escolaridad', 'genero', 'migrante', 'grupo_etnico'])}
    aux1,aux2 = data2['apellido1_'] , data1['apellido2_']
    data1['apellido2_'] = aux1
    data2['apellido1_'] = aux2
    return comparar_personas(data1, data2, umbrales)

if __name__ == '__main__':
    app.run_server(debug=True)
