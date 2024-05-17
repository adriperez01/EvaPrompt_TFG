from flask import Flask, render_template, request, redirect, session, jsonify
import datetime
import csv
import re
from openai import OpenAI
from confiDB import *
import secrets


client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

def login_usuario(correo,contrasena):

        # Verificar las credenciales del usuario en la base de datos
        db = get_db()
        cursor = db.cursor()

        select_query = "SELECT * FROM usuarios WHERE correo_electronico = %s AND password = %s"
        values = (correo, contrasena)

        print(correo)
        print(type(correo))
        print(contrasena)
        print(type(contrasena))

        try:
            cursor.execute(select_query, values)
            usuario = cursor.fetchone()
            return usuario
        except mysql.connector.Error as error:
            return jsonify({'message': f'Error al consultar en la base de datos: {error}'}), 500
        finally:
            cursor.close()

def registro_usuario(data):
    nombre = data.get('nombre')
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    if not (nombre and correo and contrasena):
        return {'message': 'Faltan datos obligatorios'}, 400

    db = get_db()
    cursor = db.cursor()

    # Verificar si el correo electrónico ya está en uso
    check_query = "SELECT * FROM usuarios WHERE correo_electronico = %s"
    cursor.execute(check_query, (correo,))
    existing_user = cursor.fetchone()

    if existing_user:
        return {'message': 'El correo electrónico ya está en uso'}, 409
    else:
        # Insertar el nuevo usuario en la base de datos
        insert_query = "INSERT INTO usuarios(nombre, correo_electronico, password) VALUES (%s, %s, %s)"
        values = (nombre, correo, contrasena)

        try:
            cursor.execute(insert_query, values)
            db.commit()
            cursor.close()
            return {'message': 'Registro exitoso'}, 200
        except mysql.connector.Error as error:
            print(error)
            return {'message': 'Error en el registro. Por favor, inténtalo de nuevo más tarde'}, 500

def obtener_columnas_dataset(csv_content):
    # Parsear el contenido CSV y extraer las columnas
    lines = csv_content.split('\n')
    headers = lines[0].split(',')
    return headers
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def parse_csv(csv_content):
    dataset = []
    lines = csv_content.split('\n')
    headers = lines[0].split(',')
    # Utilizamos csv.reader con la opción de quotechar para manejar comillas dentro de los campos
    reader = csv.reader(lines[1:], quotechar='"', delimiter=',')
    for row in reader:
        row_dict = {header: value for header, value in zip(headers, row)}
        dataset.append(row_dict)
    return dataset

import datetime

import datetime
import mysql.connector
from flask import session

def insert_datasetbd(nombre, columnaEvaluar, columnaAsociada, dataset):
    usuario = session['usuario']
    # Obtener la fecha y hora actual
    fecha_creacion = datetime.datetime.now()
    # Insertar el nuevo conjunto de datos en la base de datos
    db = get_db()
    try:
        for fila in dataset:
            if columnaEvaluar in fila and columnaAsociada in fila:
                print(fila.keys())  # Imprime las claves del diccionario fila
                print(columnaAsociada, columnaEvaluar)
                insert_query = "INSERT INTO conjuntos_datos (nombre, fecha_creacion, id_usuario_creador, columna_evaluar, columna_asociada) VALUES (%s, %s, %s, %s, %s)"
                values = (nombre, fecha_creacion, usuario[0], fila[columnaEvaluar], fila[columnaAsociada])
                cursor = db.cursor()
                cursor.execute(insert_query, values)
                db.commit()
                cursor.close()
            else:
                print("Las columnas no están presentes en la fila")
    except mysql.connector.Error as error:
        db.rollback()  # Revertir la transacción en caso de error
        print("Error al insertar datos:", error)
    finally:
        db.close()


def consulta_dataset(idusuario):

    # Verificar las credenciales del usuario en la base de datos
    db = get_db()
    cursor = db.cursor()
    select_query = "SELECT DISTINCT nombre FROM conjuntos_datos WHERE id_usuario_creador = %s"
    values = (idusuario,)
    try:
        cursor.execute(select_query, values)
        nombres = [row[0] for row in cursor.fetchall()] 
        return nombres
    except mysql.connector.Error as error:
        print(f"ERROR = {error}")
        return jsonify({'message': f'Error al consultar en la base de datos: {error}'}), 500
    finally:
        cursor.close()

# Definir función guardado_prompt
def guardado_prompt(data,priority_accuracy):
    usuario = session['usuario']
    nombre = data.get('nombre')
    datasetEvaluar = data.get('datasetEvaluar')
    tecnicaUtilizada = data.get('tecnicaUtilizada')
    accuracy = priority_accuracy
    print(accuracy)
    if not (nombre and datasetEvaluar and tecnicaUtilizada):
        return jsonify({'message': 'Faltan datos obligatorios'}), 400

    db = get_db()
    cursor = db.cursor()

    # Insertar el nuevo prompt en la base de datos
    insert_query = "INSERT INTO prompts(nombre_prompt, tecnica_utilizada, nombre_dataset, porcentaje_acierto, id_usuario) VALUES (%s, %s, %s, %s, %s)"
    values = (nombre, tecnicaUtilizada, datasetEvaluar, accuracy, usuario[0])

    try:
        cursor.execute(insert_query, values)
        db.commit()
        cursor.close()
        return True
    except mysql.connector.Error as error:
        print(error)
        return False


def generate_openai_response(user_message):
    # Lógica de solicitud a la API de OpenAI local
    response = client.chat.completions.create(
        model="local-model",  # Cambia el modelo según tus necesidades
        messages=[
            {"role": "system", "content":  "Eres un asistente virtual dedicado a tareas de clasificación, responde con una palabra."},
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

def obtener_datos_desde_bd(data):
    nombre = data.get('datasetEvaluar')
    db = get_db()
    # Ejemplo de consulta SQL
    select_query =  "SELECT columna_evaluar, columna_asociada FROM conjuntos_datos WHERE nombre = %s"
    values = (nombre,)
    # Aquí debes ejecutar la consulta y recuperar los datos de la base de datos
    datos = []
    # Suponiendo que tienes acceso a una conexión a la base de datos llamada 'db'
    cursor = db.cursor()
    cursor.execute(select_query,values)
    rows = cursor.fetchall()
    for row in rows:
        datos.append({"columna_evaluar": row[0], "columna_asociada": row[1]})
    cursor.close()

    return datos

def obtener_tags(data):
    nombre = data.get('datasetEvaluar')
    db = get_db()
    cursor = db.cursor()
    # Ejemplo de consulta SQL
    select_query =  "SELECT DISTINCT columna_asociada FROM conjuntos_datos WHERE nombre = %s"
    values = (nombre,)
    # Aquí debes ejecutar la consulta y recuperar los datos de la base de datos
    datos = []
    try:
        cursor.execute(select_query, values)
        nombres = [row[0] for row in cursor.fetchall()] 
        return nombres
    except mysql.connector.Error as error:
        print(f"ERROR = {error}")
        return jsonify({'message': f'Error al consultar en la base de datos: {error}'}), 500
    finally:
        cursor.close()

def basic_prompt(user_message,data):
    dicc = {}
    desired_tags = obtener_tags(data)
    print(desired_tags)
    count, score_tags = 0, 0
    datos = obtener_datos_desde_bd(data)
    for element in datos[0:5]:  # Aquí limitamos a 5 elementos como en tu ejemplo original
        texto = element["columna_evaluar"]
        prompt_pre = f"{user_message}"
        prompt_at = prompt_pre.replace("[ATRIBUTOS]", ", ".join(desired_tags))
        prompt = prompt_at.replace("[FRASE]", texto)
        print(prompt)
        response = generate_openai_response(prompt)
        dicc[prompt] = response
        #dicc[count] = response
        print(dicc)
        print(texto)
        print("Prediction: " + response)
        print(type(element["columna_asociada"]))
        print(element["columna_asociada"])
        columnaSE= re.sub(r"\s+", "", element["columna_asociada"])

        if response == columnaSE:
            score_tags += 1
            print("Correct")
            print([tag for tag in element.get("columna_asociada") if tag in desired_tags])
        else:
            print("Incorrect")
            print([tag for tag in element.get("columna_asociada") if tag in desired_tags])
        count += 1
        print()


    print("__________________")
    print(f"Priority Accuracy: {score_tags/count}")
    priority_accuracy = score_tags / count
    
    return [priority_accuracy, dicc]