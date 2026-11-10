import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

load_dotenv(override=True)

app = Flask(__name__)

# Conexion a la BD
app.config['MYSQL_HOST'] = os.environ['DB_HOST']
app.config['MYSQL_USER']= os.environ['DB_USER']
app.config['MYSQL_PASSWORD'] = os.environ['DB_PASSWORD']
app.config['MYSQL_DB'] = os.environ['DB_NAME']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def inicio():
    #return f"Conexion  BD biblioteca funcionando!!!!"
    return jsonify({"mensaje":"API Biblioteca funcionando"})

# GET /api/libros/
@app.route('/api/libros/', methods = ['GET'])
def listar_libros():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM libros"
    cursor.execute(sql)
    libros = cursor.fetchall()
    cursor.close()
    return jsonify(libros)

#GET /api/libros/<id>
@app.route('/api/libros/<int:id>', methods = ['GET'])
def listar_libro(id):
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM libros WHERE id = %s"
    cursor.execute(sql,(id,))
    libro = cursor.fetchone()
    cursor.close()

    if libro is None:
        return jsonify({"error": "Libro no encoentrado"}), 404
    return jsonify(libro)

# POST /api/libros   para registrar un libro
@app.route('/api/libros', methods=['POST'])
def registrar_libro():
    datos = request.get_json(silent=True)

    titulo = datos.get('titulo')
    autor = datos.get('autor')
    stock = datos.get('stock')

    cursor = mysql.connection.cursor()
    sql = "INSERT INTO libros (titulo, autor, stock) VALUES (%s, %s, %s)"
    cursor.execute(sql, (titulo, autor, stock))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje":"Libro registrado"}),201
    

if __name__ == '__main__':
    app.run(debug=True)    