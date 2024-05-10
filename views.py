from flask import Flask, Blueprint, render_template, request, redirect, session, jsonify
import datetime
from confiDB import *
from services import *
import csv

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
        registro_usuario(data)
        try:
            return jsonify({'message': 'Usuario creado correctamente'}), 200
        except mysql.connector.Error as error:
            return jsonify({'message': 'Error al registrar usuario'}), 400

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
            
            #Insertar datos en BD
            insert_datasetbd(nombre, columnaEvaluar, columnaAsociada,dataset)

            # Devolver las columnas y el dataset procesado
            return jsonify({'columnas': columnas, 'dataset': dataset}), 200
        
    return jsonify({'error': 'Método no permitido'}), 405

@visual_bp.route('/evaluador', methods=['POST','GET'])
def chat():
    if request.method == 'GET':   
        if 'usuario' in session:
            usuario = session['usuario']
            print(usuario[0])
            return render_template('evaluator.html')
        else:
            return redirect('/')

    elif request.method == 'POST':
        data = session.get(dataset)
        dato = request.json
        user_message = dato['message']
        resultados = basic_prompt(user_message, data)
        priority_accuracy = resultados[0]

        try:
            bot_message = resultados[2]
            response = {'message': bot_message, 'priority_accuracy': priority_accuracy}
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': str(e)})