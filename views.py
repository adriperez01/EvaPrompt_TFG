from flask import Flask, Blueprint, render_template, request, redirect, session, jsonify
import datetime
from confiDB import *
from services import *
import csv
import plotly.express as px
import pandas as pd
import plotly.io as pio

visual_bp = Blueprint("visual",__name__)

@visual_bp.route('/')
def index():
    return render_template('./index.html')

@visual_bp.route('/login', methods=['POST','GET'])
def log():
    if request.method == 'GET':
        return render_template('logpage.html')
    elif request.method == 'POST':
        correo = request.form['correo_electronico']
        contrasena = request.form['contrasena']
        usuario = login_usuario(correo,contrasena)
        if usuario:
            session['usuario'] = usuario
            return jsonify({'message': 'Inicio de sesión exitoso'}), 200
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401
        
@visual_bp.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('dashboard.html')
    else:
        return redirect('/')

@visual_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

@visual_bp.route('/registro', methods=['POST','GET'])
def registro():        
    if request.method == 'GET':
        return render_template('regpage.html')
    elif request.method == 'POST':
        data = request.get_json()
        try:
            response, status_code = registro_usuario(data)
            return jsonify(response), status_code
        except Exception as e:
            print(f"Error al registrar usuario: {str(e)}")
            return jsonify({'message': 'Error al registrar usuario'}), 500

@visual_bp.route('/upload_dataset', methods=['POST','GET'])
def upload_dataset():  
    if request.method == 'GET':   
        if 'usuario' in session:
            usuario = session['usuario']
            print(usuario[0])
            return render_template('upload_dataset.html')
        else:
            return redirect('/')

    elif request.method == 'POST':
        # Insertar los datos en la tabla conjuntos_dato
        nombre = request.form.get('nombre')
        columnaEvaluar =  request.form.get('columnaEvaluar')
        columnaAsociada = request.form.get('columnaAsociada')
        # Verificar si se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó ningún archivo CSV'}), 400
        
        file = request.files['file']
        
        # Verificar si se seleccionó un archivo
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo CSV'}), 400

        # Procesar el archivo CSV
        if file and allowed_file(file.filename):
            # Leer el contenido del archivo
            csv_content = file.read().decode('utf-8')
            
            # Obtener las columnas del dataset
            columnas = obtener_columnas_dataset(csv_content)
            
            # Parsear el contenido CSV
            dataset = parse_csv(csv_content)
            session['dataset'] = dataset
            
            #Insertar datos en BD
            insert_datasetbd(nombre, columnaEvaluar, columnaAsociada,dataset)

            # Devolver las columnas y el dataset procesado
            return jsonify({'columnas': columnas, 'dataset': dataset}), 200
        
    return jsonify({'error': 'Método no permitido'}), 405

@visual_bp.route('/v1/chat', methods=['POST','GET'])
def chat():
    if request.method == 'GET':   
        if 'usuario' in session:
            usuario = session['usuario']
            consulta_dataset(usuario[0])
            return render_template('evaluator.html')
        else:
            return redirect('/')

    elif request.method == 'POST':
        data = request.get_json()
        prompt = []
        bot_message = []
        print(data)
        dato = request.json
        user_message = dato['message']
        resultados = basic_prompt(user_message, data)
        for clave, valor in resultados[1].items():
            prompt.append(clave)
            bot_message.append(valor)
        priority_accuracy = resultados[0]
        guardado_prompt(data,priority_accuracy)
        try:
            response = {'message': bot_message, 'priority_accuracy': priority_accuracy, 'prompt': prompt}
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': str(e)})

@visual_bp.route('/generate', methods=['POST','GET'])
def generate():
    if request.method == 'GET':   
        if 'usuario' in session:
            usuario = session['usuario']
            consulta_dataset(usuario[0])
            return render_template('generador.html')
        else:
            return redirect('/')
    data = request.json
    prompt = data.get('prompt', '')

    try:
        response = generate_openai_response(prompt)
        generated_text = response['choices'][0]['text']
        
        return jsonify({'output': generated_text})
    except Exception as e:
        print(f'Error generating prompt: {e}')
        return jsonify({'error': 'Error generating prompt'}), 500        

@visual_bp.route('/historial_prompts', methods=['GET', 'POST'])
def historial_prompts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT nombre_prompt, tecnica_utilizada, porcentaje_acierto FROM prompts"
    cursor.execute(query)
    prompts = cursor.fetchall()
    cursor.close()
    
    # Crear DataFrame con los datos
    df = pd.DataFrame(prompts)
    
    # Obtener los valores únicos de técnicas para los filtros
    tecnicas = df['tecnica_utilizada'].unique()

    tecnica_filtro = request.form.get('tecnica')
    excluir_prompts = request.form.getlist('excluir_prompts')
    
    if tecnica_filtro:
        df = df[df['tecnica_utilizada'] == tecnica_filtro]
    
    if excluir_prompts:
        df = df[~df['nombre_prompt'].isin(excluir_prompts)]
    
    # Crear la gráfica con Plotly y asignar colores según la técnica utilizada
    fig = px.bar(
        df, 
        x='nombre_prompt', 
        y='porcentaje_acierto', 
        color='tecnica_utilizada',
        title='Porcentajes de Acierto de Prompts'
    )
    
    # Ajustar la escala y los nombres de los ejes
    fig.update_layout(
        xaxis_title='Nombre del Prompt',
        yaxis_title='Porcentaje de Acierto (%)',
        yaxis=dict(range=[0, 1]),  # Asegurarse de que la escala del eje Y vaya de 0 a 100
        title=dict(x=0.5)  # Centrar el título
    )
    
    # Convertir la gráfica a HTML
    graph_html = pio.to_html(fig, full_html=False)
    
    return render_template('historial_prompts.html', graph_html=graph_html, tecnicas=tecnicas, prompts=prompts, tecnica_filtro=tecnica_filtro, excluir_prompts=excluir_prompts)


