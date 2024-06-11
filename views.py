from flask import Flask, Blueprint, render_template, request, redirect, session, jsonify, send_file, make_response
import io
import datetime
from confiDB import *
from services import *
import csv
import plotly.express as px
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

@visual_bp.route('/redactor_prompts')
def redactor_prompts():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('redactor_prompts.html')
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

@visual_bp.route('/v1/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'GET':
        if 'usuario' in session:
            usuario = session['usuario']
            consulta_dataset(usuario[0])
            return render_template('evaluator.html')
        else:
            return redirect('/')
    elif request.method == 'POST':
        try:
            data = request.json  # Obtener los datos JSON de la solicitud
            user_message = data.get('message')  # Obtener el mensaje del usuario
            if user_message is None:
                return jsonify({'error': 'No se proporcionó un mensaje'}), 400

            prompt, bot_message = [], []
            resultados = basic_prompt(user_message, data)
            for clave, valor in resultados[4].items():
                prompt.append(clave)
                bot_message.append(valor)
            priority_accuracy = resultados[0]
            precision = resultados[1]
            recall = resultados[2]
            f1_score = resultados[3]
            guardado_prompt(data, priority_accuracy, precision, recall, f1_score)

            response = {'message': bot_message, 'priority_accuracy': priority_accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1_score, 'prompt': prompt}
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


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

@visual_bp.route('/estadisticas', methods=['GET', 'POST'])
def estadisticas():
    # Redirección si el usuario no está autenticado
    if not session.get('usuario'):
        return redirect('/')
    usuario = session['usuario']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT nombre_prompt, tecnica_utilizada, nombre_dataset, porcentaje_acierto, recall, f1, precc FROM prompts WHERE id_usuario = %s"
    values = (usuario[0],)
    cursor.execute(query, values)
    prompts = cursor.fetchall()
    cursor.close()
    
    # Crear DataFrame con los datos
    df = pd.DataFrame(prompts)
    
    # Obtener los valores únicos de técnicas, datasets y métricas para los filtros
    tecnicas = df['tecnica_utilizada'].unique()
    datasets = df['nombre_dataset'].unique()
    metricas = ['porcentaje_acierto', 'recall', 'f1', 'precc']
    
    tecnica_filtro = request.form.get('tecnica')
    dataset_filtro = request.form.get('dataset')
    metrica_filtro = request.form.get('metrica')
    excluir_prompts = request.form.getlist('excluir_prompts')
    incluir_prompts = request.form.getlist('incluir_prompts')
        # Si no hay prompts para mostrar, enviar un mensaje
    if df.empty:
        graph_html = '<p>No hay prompts para mostrar.</p>'
        
    if dataset_filtro:
        df = df[df['nombre_dataset'] == dataset_filtro]
    
    if tecnica_filtro:
        df = df[df['tecnica_utilizada'] == tecnica_filtro]
    
    # Excluir prompts seleccionados
    if excluir_prompts:
        df = df[~df['nombre_prompt'].isin(excluir_prompts)]
    
    # Incluir prompts previamente excluidos
    if incluir_prompts:
        excluidos_df = pd.DataFrame([p for p in prompts if p['nombre_prompt'] in incluir_prompts])
        df = pd.concat([df, excluidos_df], ignore_index=True)
    
    else:
        # Crear la gráfica combinada con Plotly
        fig = go.Figure()
        
        if metrica_filtro:
            metricas = [metrica_filtro]
        
        for tecnica in df['tecnica_utilizada'].unique():
            df_tecnica = df[df['tecnica_utilizada'] == tecnica]
            
            for metrica in metricas:
                fig.add_trace(go.Bar(
                    x=df_tecnica['nombre_prompt'],
                    y=df_tecnica[metrica],
                    name=f'{tecnica} - {metrica.capitalize()}',
                ))
        
        fig.update_layout(
            barmode='group',
            xaxis_title='Nombre del Prompt',
            yaxis_title='Valor',
            title='Métricas de Evaluación de Prompts',
            title_x=0.5
        )
        
        # Convertir la gráfica a HTML
        graph_html = pio.to_html(fig, full_html=False)
    
    # Prompts excluidos (no incluidos en el DataFrame filtrado)
    prompts_excluidos = [p for p in prompts if p['nombre_prompt'] not in df['nombre_prompt'].values]
    
    return render_template(
        'estadisticas.html', 
        graph_html=graph_html,
        tecnicas=tecnicas, 
        datasets=datasets, 
        metricas=metricas,
        prompts=prompts, 
        tecnica_filtro=tecnica_filtro, 
        dataset_filtro=dataset_filtro,
        metrica_filtro=metrica_filtro,
        excluir_prompts=excluir_prompts, 
        prompts_excluidos=prompts_excluidos
    )

@visual_bp.route('/manage_datasets')
def manage_datasets():
    if 'usuario' in session:
        usuario = session['usuario']
        datasets = consulta_dataset(usuario[0])
        return render_template('manage_datasets.html', datasets=datasets)
    else:
        return redirect('/')

@visual_bp.route('/eliminar_dataset', methods=['POST'])
def eliminar_dataset():
    if 'usuario' in session:
        usuario = session['usuario']
        data = request.get_json()
        nombre_dataset = data['nombre']
        exito = eliminar_dataset_db(nombre_dataset, usuario[0])
        if exito:
            return jsonify({'message': 'Dataset eliminado exitosamente'}), 200
        else:
            return jsonify({'message': 'Error al eliminar el dataset'}), 500
    else:
        return jsonify({'message': 'No autorizado'}), 401

@visual_bp.route('/previsualizar_dataset', methods=['POST'])
def previsualizar_dataset():
    if 'usuario' in session:
        data = request.get_json()
        nombre_dataset = data['nombre']
        dataset = obtener_datos_completos_dataset(nombre_dataset)
        return jsonify(dataset), 200
    else:
        return jsonify({'message': 'No autorizado'}), 401

@visual_bp.route('/manage_prompts')
def manage_prompts():
    if 'usuario' in session:
        usuario = session['usuario']
        prompts = consulta_prompt(usuario[0])
        return render_template('manage_prompts.html', prompts = prompts)
    else:
        return redirect('/')
    

@visual_bp.route('/eliminar_prompt', methods=['POST'])
def eliminar_prompt():
    if 'usuario' in session:
        usuario = session['usuario']
        data = request.get_json()
        nombre_prompt = data['nombre']
        exito = eliminar_prompt_db(nombre_prompt, usuario[0])
        if exito:
            return jsonify({'message': 'Prompt eliminado exitosamente'}), 200
        else:
            return jsonify({'message': 'Error al eliminar el prompt'}), 500
    else:
        return jsonify({'message': 'No autorizado'}), 401

@visual_bp.route('/renombrar_prompt', methods=['POST'])
def renombrar_prompt():
    if 'usuario' in session:
        usuario = session['usuario']
        data = request.json
        nuevo_nombre = data['nuevo_nombre']
        antiguo_nombre = data['antiguo_nombre']
        print(type(nuevo_nombre))
        print(type(antiguo_nombre))

        # Aquí realizas la actualización en la base de datos
        db = get_db()
        cursor = db.cursor()
        try:
            update_query = "UPDATE prompts SET nombre_prompt = %s WHERE nombre_prompt = %s AND id_usuario = %s"
            cursor.execute(update_query, (nuevo_nombre, antiguo_nombre, usuario[0]))
            db.commit()
            return jsonify({'message': 'El prompt ha sido renombrado exitosamente'})
        except mysql.connector.Error as error:
            db.rollback()
            return jsonify({'message': f'Error al renombrar el prompt en la base de datos: {error}'}), 500
        finally:
            cursor.close()
    else:
        return redirect('/')
@visual_bp.route('/renombrar_dataset', methods=['POST'])
def renombrar_dataset():
    if 'usuario' in session:
        usuario = session['usuario']
        data = request.json
        nuevo_nombre = data['nuevo_nombre']
        antiguo_nombre = data['antiguo_nombre']

        db = get_db()
        cursor = db.cursor()

        try:
            # Deshabilitar temporalmente las verificaciones de claves foráneas
            cursor.execute("SET foreign_key_checks = 0")

            # Actualizar la tabla hija (prompts)
            update_query_prompts = """
                UPDATE prompts 
                SET nombre_dataset = %s 
                WHERE nombre_dataset = %s AND id_usuario = %s
            """
            cursor.execute(update_query_prompts, (nuevo_nombre, antiguo_nombre, usuario[0]))

            # Actualizar la tabla padre (conjuntos_datos)
            update_query_conjuntos_datos = """
                UPDATE conjuntos_datos 
                SET nombre = %s 
                WHERE nombre = %s AND id_usuario_creador = %s
            """
            cursor.execute(update_query_conjuntos_datos, (nuevo_nombre, antiguo_nombre, usuario[0]))

            # Confirmar transacción
            db.commit()

        except mysql.connector.Error as error:
            # Revertir transacción en caso de error
            db.rollback()
            return jsonify({'message': f'Error al renombrar el dataset en la base de datos: {error}'}), 500
        
        finally:
            # Volver a habilitar las verificaciones de claves foráneas
            cursor.execute("SET foreign_key_checks = 1")
            cursor.close()

        return jsonify({'message': 'El dataset ha sido renombrado exitosamente'})
    else:
        return redirect('/')

    
@visual_bp.route('/eliminar_fila', methods=['POST'])
def eliminar_fila():
    if 'usuario' in session:
        data = request.get_json()
        nombre_dataset = data['nombre']
        fila_id = data['fila_id']
        print(fila_id)
        try:
            db = get_db()
            cursor = db.cursor()
            delete_prompts_query = "DELETE FROM prompts WHERE nombre_dataset = %s"
            cursor.execute(delete_prompts_query, (nombre_dataset,))
            db.commit()
            delete_row_query = "DELETE FROM conjuntos_datos WHERE id_conjunto_datos = %s"
            cursor.execute(delete_row_query, (fila_id,))
            db.commit()

            cursor.close()
            return jsonify({'message': 'Fila eliminada correctamente.'}), 200
        except mysql.connector.Error as error:
            print(f"ERROR = {error}")
            return jsonify({'message': f'Error al eliminar la fila: {error}'}), 500
    else:
        return jsonify({'message': 'No autorizado'}), 401
