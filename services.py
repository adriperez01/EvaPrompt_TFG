from flask import Flask, render_template, request, redirect, session, jsonify
import datetime
from confiDB import *
import secrets


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

