from flask import Flask, render_template, request, redirect, session, jsonify
from views import visual_bp
from services import *
from confiDB import *
import os
import secrets


app = Flask(__name__)
app.register_blueprint(visual_bp)
app.secret_key = secrets.token_hex(16)

# Configuración de la base de datos
app.config['DB_HOST'] = 'localhost'
app.config['DB_PORT'] = 3306
app.config['DB_USER'] = 'root'
app.config['DB_PASSWORD'] = 'root'
app.config['DB_NAME'] = 'evap1'

with app.app_context():
    dir = os.path.realpath(os.getcwd())
    execute_sql_file(dir + os.sep + "schema.sql")

@app.route('/obtener_dataset', methods=['GET'])
def obtener_dataset():
    usuario = session['usuario']
    print(usuario[0])
    id_usuario = usuario[0]  # Aquí deberías proporcionar el ID de usuario adecuado
    nombres = consulta_dataset(id_usuario)
    
    # Crear la respuesta JSON
    response = {'nombres': nombres}
    return jsonify(response)

@app.route('/guardar_prompt', methods=['POST'])
def guardar_prompt():
    data = request.json
    print("Datos recibidos:", data)  # Imprimir los datos recibidos del formulario

    if guardado_prompt(data):
        print("Prompt guardado correctamente")
        return jsonify({'message': 'Prompt guardado correctamente'}), 200
    else:
        print("Error al guardar el prompt")
        return jsonify({'message': 'Error al guardar el prompt'}), 500

if __name__ == "__main__":
    app.run(debug=True)
