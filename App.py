import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
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

@app.route('/libros')
def lista_de_libros():
    return render_template("lista_libros.html")

@app.route('/registrar-libro')
def registro_de_libros():
    return render_template("registrar_libro.html")

@app.route('/buscar-libro')
def buscar_libro():
    return render_template("buscar_libro.html")

@app.route('/modificar-libro/<int:id>')
def pagina_modificar_libro(id):
    return render_template("modificar_libro.html",id=id)


@app.route('/prestamos')
def listado_de_prestamos():
    return render_template("Lista-prestamos.html")


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
        return jsonify({"error": "Libro no encontrado"}), 404
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

# PUT modificaar un libro con id
# PUT /api/libros/<id>
@app.route('/api/libros/<int:id>', methods = ['PUT'])
def modificar_libro(id):
    datos = request.get_json(silent=True)

    titulo = datos.get('titulo')
    autor = datos.get('autor')
    stock = datos.get('stock')

    cursor = mysql.connection.cursor()
    sql = "UPDATE libros SET titulo = %s, autor = %s, stock = %s WHERE id = %s"
    cursor.execute(sql, (titulo, autor, stock, id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje": "libro modificado", "id": id}),200

# DELETE elimina un libro con id
# DELETE /api/libros/id
@app.route('/api/libros/<int:id>', methods = ['DELETE'])
def eliminar_libro(id):
    #verificar si el libro tiene prestamos
    sql = "SELECT count(*) as total FROM prestamos WHERE libro_id = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (id,))

    resultado = cursor.fetchone()
    if resultado['total'] > 0:
        return jsonify({"error": "no se puede eliminar el libro"}),400

    sql = "DELETE FROM libros WHERE id = %s"
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Libro eliminado", "id":id}),200

# GET /api/prestamos/
@app.route('/api/prestamos', methods=['GET'])
def listar_prestamos():
    cursor = mysql.connection.cursor()
    #sql = "SELECT * FROM prestamos"
    sql = """SELECT p.id, p.libro_id, l.titulo AS libro, p.estudiante, p.fecha_prestamo, p.estado, p.fecha_devolucion
             FROM prestamos p
             INNER JOIN libros l ON l.id = p.libro_id
             ORDER BY p.id"""
    datos = cursor.execute(sql)
    prestamos = cursor.fetchall()
    return jsonify(prestamos)


#POST /api/prestamos
@app.route('/api/prestamos', methods=['POST'])
def registrar_prestamo():
    datos = request.get_json(silent=True)
    libro_id = datos.get('libro_id')
    estudiante = datos.get('estudiante')

    cursor = mysql.connection.cursor()

    sql = "SELECT stock FROM libros WHERE id = %s FOR UPDATE"
    cursor.execute(sql,(libro_id,))
    libro = cursor.fetchone()

    if libro['stock'] <= 0:
        mysql.connection.rollback()
        return jsonify({"error":"No hay ejemplares"}),409

    sql = "UPDATE libros SET stock = stock - 1  WHERE id = %s AND stock > 0"
    cursor.execute(sql,(libro_id,))

    sql = "INSERT INTO prestamos (libro_id, estudiante) VALUES (%s, %s)"
    cursor.execute(sql,(libro_id,estudiante))

    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje":"Prestamo registrado"}),201

# PATCH /api/prestamos/<id>
@app.route('/api/prestamos/<int:id>', methods = ['PATCH'])
def devolver_prestamos(id):
    #datos = request.get_json(silent=True)
    cursor = mysql.connection.cursor();

    sql="SELECT libro_id FROM prestamos WHERE id = %s"
    cursor.execute(sql,(id,))
    prestamo_inicial = cursor.fetchone()
    libro_id = prestamo_inicial['libro_id']

    sql = "SELECT id FROM libros WHERE id = %s FOR UPDATE"
    cursor.execute(sql,(libro_id,))

    sql = "SELECT estado FROM prestamos WHERE id = %s FOR UPDATE"
    cursor.execute(sql,(id,))

    prestamo = cursor.fetchone()

    if prestamo['estado'] == 'devuelto':
        mysql.connection.rollback()
        return jsonify({"error":"Pretamos ya devuelto"}),409

    sql = "UPDATE prestamos SET estado = 'devuelto', fecha_devolucion = NOW() WHERE id = %s "
    cursor.execute(sql, (id,))

    sql = "UPDATE libros SET stock = stock + 1 WHERE id = %s"
    cursor.execute(sql,(libro_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje":"Devolucion registrada correctamente", "id":id}),200 


@app.route('/biblioteca')
def pagina_biblioteca():
    return render_template('prestamo.html')




if __name__ == '__main__':
    app.run(debug=True)    