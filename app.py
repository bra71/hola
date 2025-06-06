from config.conexion import conexion
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "wazza"  # Use env variable in production

def mostrarTodo():
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM tb_cliente')
    clientes = cursor.fetchall()
    cursor.close()
    return clientes

@app.route('/insertar', methods=['POST'])
def insertar():
    nombre = request.form['txtnombre']
    nit = request.form['txtnit']
    cursor = conexion.cursor()
    sql = "INSERT INTO tb_cliente (nombre, nit) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, nit))
    conexion.commit()
    cursor.close()
    clientes = mostrarTodo()
    mensaje = "Registro insertado correctamente"
    return render_template('registrar.html', mensaje=mensaje, clientes=clientes)

@app.route('/')
def index():
    mensaje = "Bienvenido a la pagina de ventas, B.L.C.V"
    clientes = mostrarTodo()
    return render_template('registrar.html', mensaje=mensaje, clientes=clientes)

@app.route('/actualizar/<id>')
def actualizar(id):
    cursor = conexion.cursor()
    sql = "SELECT * FROM tb_cliente WHERE id_cliente=%s"
    cursor.execute(sql, (id,))
    dato = cursor.fetchone()
    cursor.close()
    return render_template('actualizar.html', dato=dato)

@app.route('/actualizar_cliente', methods=['POST'])
def actualizar_cliente():
    id = request.form['id']
    nombre = request.form['nombre']
    nit = request.form['nit']
    cursor = conexion.cursor()
    sql = "UPDATE tb_cliente SET nombre = %s, nit = %s WHERE id_cliente = %s"
    cursor.execute(sql, (nombre, nit, id))
    conexion.commit()
    cursor.close()
    return redirect('/')

@app.route('/eliminar/<id>')
def eliminar(id):
    cursor = conexion.cursor()
    sql = "DELETE FROM tb_cliente WHERE id_cliente=%s"
    cursor.execute(sql, (id,))
    conexion.commit()
    cursor.close()
    return redirect('/')

@app.route('/comprar', methods=['POST'])
def insertarCompra():
    id = request.form['id']
    producto = request.form['producto']  # Make sure HTML uses 'producto'
    cantidad = request.form['cantidad']
    costo = request.form['costo']
    cursor = conexion.cursor()
    sql = "INSERT INTO tb_compra (tb_cliente_id_cliente, producto, cantidad, costo) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (id, producto, cantidad, costo))
    conexion.commit()
    cursor.close()
    return redirect('/')

@app.route('/vercompras/<id>', methods=['GET'])
def vercompras(id):
    cursor = conexion.cursor()
    sql = "SELECT * FROM tb_compra WHERE tbcliente_id_cliente=%s"
    cursor.execute(sql, (id,))
    datos = cursor.fetchall()
    cursor.close()
    return render_template('vercompras.html', datos=datos)

def mostrarCliente(id):
    cursor = conexion.cursor()
    sql = "SELECT * FROM tb_cliente WHERE id_cliente=%s"
    cursor.execute(sql, (id,))
    dato = cursor.fetchone()
    cursor.close()
    return dato

if __name__ == '__main__':
    app.run(debug=True)
