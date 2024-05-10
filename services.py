from flask import Flask, render_template, request, redirect, session, jsonify
import datetime
from openai import OpenAI
from confiDB import *
import secrets


client = OpenAI(base_url="http://localhost:3306/evaluador", api_key="not-needed")

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
    print(nombre)
    print(type(nombre))
    print(correo)
    print(type(correo))
    print(contrasena)
    print(type(contrasena))

    if not (nombre and correo and contrasena):
        return jsonify({'message': 'Faltan datos obligatorios'}), 400

    fecha_creacion = datetime.datetime.now()
    print(fecha_creacion)
    print(type(fecha_creacion))

    db = get_db()
    cursor = db.cursor()

    # Insertar el nuevo usuario en la base de datos
    insert_query = "INSERT INTO usuarios(nombre, correo_electronico, password, fecha_creacion) VALUES (%s, %s, %s, %s)"
    values = (nombre, correo, contrasena, fecha_creacion)

    try:
        cursor.execute(insert_query, values)
        db.commit()
        cursor.close()
        pass
    except mysql.connector.Error as error:
        print(error)

def obtener_columnas_dataset(csv_content):
    # Parsear el contenido CSV y extraer las columnas
    lines = csv_content.split('\n')
    headers = lines[0].split(',')
    return headers
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def parse_csv(csv_content):
    # Parsear el contenido CSV y convertirlo a una lista de diccionarios
    dataset = []
    lines = csv_content.split('\n')
    headers = lines[0].split(',')
    for line in lines[1:]:
        values = line.split(',')
        row = {header: value for header, value in zip(headers, values)}
        dataset.append(row)
    return dataset

import datetime

def insert_datasetbd(nombre, columnaEvaluar, columnaAsociada, dataset):
    usuario = session['usuario']
    # Obtener la fecha y hora actual
    fecha_creacion = datetime.datetime.now()
    # Insertar el nuevo conjunto de datos en la base de datos
    db = get_db()
    cursor = db.cursor()
    insert_query = "INSERT INTO conjuntos_datos (nombre, fecha_creacion, id_usuario_creador, columna_evaluar, columna_asociada) VALUES (%s, %s, %s, %s, %s)"
    values = (nombre, fecha_creacion, usuario[0], columnaEvaluar, columnaAsociada)
    print(columnaAsociada,columnaEvaluar)
    print(type(columnaAsociada))

    try:
        cursor.execute(insert_query, values)
        dataset_id = cursor.lastrowid  # Obtener el ID del dataset insertado
        
        # Iterar sobre el dataset y guardar los datos en la tabla datos_columnas
        for fila in dataset:
            if columnaEvaluar in fila and columnaAsociada in fila:
                print(fila.keys())  # Imprime las claves del diccionario fila
                print(columnaAsociada, columnaEvaluar)
                insert_data_query = "INSERT INTO datos_columnas (dataset_id, dato_evaluado, dato_asociado) VALUES (%s, %s, %s)"
                data_values = (dataset_id, fila[columnaEvaluar], fila[columnaAsociada])
                cursor.execute(insert_data_query, data_values)
        else:
            print("Las columnas no están presentes en la fila")
        db.commit()
    except mysql.connector.Error as error:
        db.rollback()  # Revertir la transacción en caso de error
        print(error)
    finally:
        cursor.close()



def generate_openai_response(user_message):
    # Lógica de solicitud a la API de OpenAI local
    response = client.chat.completions.create(
        model="local-model",  # Cambia el modelo según tus necesidades
        messages=[
            {"role": "system", "content":  "Eres un analizador de sentimientos, responde con UNA SOLA PALABRA."},
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content

desired_tags =  ['Positivo', 'Neutral', 'Negativo']

def basic_prompt(user_message, data):
    dicc = {}
    count, score_tags = 0, 0
    for element in data[0:5]:
        texto = element['Texto']
        prompt_pre = f"{user_message}"
        prompt_at = prompt_pre.replace("[ATRIBUTOS]", ", ".join(desired_tags))
        prompt = prompt_at.replace("[FRASE]",texto)
        print(prompt)

        response = generate_openai_response(prompt)
        dicc[count] = response
        print(dicc)
        print(texto)
        print("Prediction: " + response)

        if response == element['Sentimiento']:
            score_tags += 1
            print("Correct")
            print([tag for tag in element.get('Sentimiento') if tag in desired_tags])
        else:
            print("Incorrect")
            print([tag for tag in element.get('Sentimiento') if tag in desired_tags])
        count += 1
        print()

    print("__________________")
    print(f"Priority Accuracy: {score_tags/count}")
    priority_accuracy = score_tags / count
    return [priority_accuracy, prompt, response]