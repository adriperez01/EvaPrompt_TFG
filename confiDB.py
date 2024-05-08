import mysql.connector
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME']
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)


def execute_sql_file(filename):
    with current_app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Leer el contenido del archivo SQL
        with open(filename, 'r') as file:
            sql_queries = file.read()

        # Dividir las consultas por punto y coma para ejecutarlas por separado
        queries = sql_queries.split(';')

        # Ejecutar cada consulta
        for query in queries:
            if query.strip():  # Verificar que la consulta no esté vacía
                try:
                    cursor.execute(query)
                except mysql.connector.Error as err:
                    if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                        print(f"La tabla ya existe: {err}")
                    else:
                        print(f"Error al ejecutar la consulta: {err}")

        db.commit()
        cursor.close()
