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


if __name__ == "__main__":
    app.run(debug=True)
