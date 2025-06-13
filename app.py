from config.conexion import conexion
from flask import Flask, render_template, request, redirect, session, make_response
from fpdf import FPDF
import hashlib

app = Flask(__name__)
app.secret_key = "admin"

def mostrarTodo():
    try:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM tb_cliente')
        clientes = cursor.fetchall()
        cursor.close()
        return clientes
    except Exception as e:
        print(f"Error al obtener todos los clientes: {e}")
        return []

def mostrarCliente(id):
    try:
        cursor = conexion.cursor()
        sql = 'SELECT * FROM tb_cliente WHERE id_cliente=%s'
        cursor.execute(sql, (id,))
        datos = cursor.fetchone()
        cursor.close()
        return datos
    except Exception as e:
        print(f"Error al obtener el cliente con ID {id}: {e}")
        return None

@app.route('/')
def index():
    mensaje = "Bienvenido a la página de ventas, B.L.C.V"
    clientes = mostrarTodo()
    return render_template('registrar.html', mensaje=mensaje, clientes=clientes)

@app.route('/insertar', methods=['POST'])
def insertar():
    nombre = request.form['txtnombre']
    nit = request.form['txtnit']
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO tb_cliente (nombre, nit) VALUES (%s, %s)"
        cursor.execute(sql, (nombre, nit))
        conexion.commit()
        cursor.close()
        clientes = mostrarTodo()
        mensaje = "Registro insertado exitosamente"
        return render_template('registrar.html', mensaje=mensaje, clientes=clientes)
    except Exception as e:
        print(f"Error al insertar cliente: {e}")
        return "Error al insertar el cliente", 500

@app.route('/actualizar/<id>')
def actualizar(id):
    try:
        cursor = conexion.cursor()
        sql = "SELECT * FROM tb_cliente WHERE id_cliente=%s"
        cursor.execute(sql, (id,))
        dato = cursor.fetchone()
        cursor.close()
        return render_template('actualizar.html', dato=dato)
    except Exception as e:
        print(f"Error al obtener datos del cliente para actualizar: {e}")
        return "Error al obtener datos del cliente", 500

@app.route('/actualizar_cliente', methods=['POST'])
def actualizar_cliente():
    id = request.form['id']
    nombre = request.form['nombre']
    nit = request.form['nit']
    try:
        cursor = conexion.cursor()
        sql = "UPDATE tb_cliente SET nombre = %s, nit = %s WHERE id_cliente = %s"
        cursor.execute(sql, (nombre, nit, id))
        conexion.commit()
        cursor.close()
        return redirect('/')
    except Exception as e:
        print(f"Error al actualizar cliente: {e}")
        return "Error al actualizar el cliente", 500

@app.route('/eliminar/<id>')
def eliminar(id):
    try:
        cursor = conexion.cursor()
        sql = "DELETE FROM tb_cliente WHERE id_cliente=%s"
        cursor.execute(sql, (id,))
        conexion.commit()
        cursor.close()
        return redirect('/')
    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
        return "Error al eliminar el cliente", 500

@app.route('/comprar/<id>')
def comprar(id):
    datos = mostrarCliente(id)
    return render_template('comprar.html', id=id, datos=datos)

@app.route('/comprar', methods=['POST'])
def insertarCompra():
    id = request.form['id']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    costo = request.form['costo']
    try:
        cursor = conexion.cursor()
        sql = "INSERT INTO tb_compra (tb_cliente_id_cliente, producto, cantidad, costo) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (id, producto, cantidad, costo))
        conexion.commit()
        cursor.close()
        return redirect('/')
    except Exception as e:
        print(f"Error al insertar compra: {e}")
        return "Error al insertar la compra", 500

@app.route('/vercompras/<id>', methods=['GET'])
def vercompras(id):
    try:
        cursor = conexion.cursor()
        sql = "SELECT * FROM tb_compra WHERE tb_cliente_id_cliente=%s"
        cursor.execute(sql, (id,))
        datos = cursor.fetchall()
        cursor.close()
        return render_template('vercompras.html', datos=datos)
    except Exception as e:
        print(f"Error al obtener compras del cliente: {e}")
        return "Error al obtener las compras", 500

@app.route('/buscar', methods=['GET'])
def buscar():
    buscar = request.args.get('txtbuscar')
    try:
        cursor = conexion.cursor()
        sql = "SELECT * FROM tb_cliente WHERE nombre LIKE %s"
        cursor.execute(sql, (buscar + '%',))
        datos = cursor.fetchall()
        cursor.close()
        return render_template('registrar.html', clientes=datos)
    except Exception as e:
        print(f"Error al buscar clientes: {e}")
        return "Error al buscar clientes", 500

@app.route('/reporte/<id>')
def generar_pdf(id):
    try:
        cursor = conexion.cursor()
        sql = """
        SELECT c.nombre, c.nit, co.producto, co.cantidad, co.costo
        FROM tb_compra co
        INNER JOIN tb_cliente c ON co.tb_cliente_id_cliente = c.id_cliente
        WHERE co.tb_cliente_id_cliente = %s
        """
        cursor.execute(sql, (id,))
        datos = cursor.fetchall()
        cursor.close()

        if not datos:
            return "No se encontraron compras para este cliente", 404

        nombre_cliente = datos[0][0]
        nit_cliente = datos[0][1]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="REPORTE DE COMPRAS", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Cliente: {nombre_cliente}", ln=True)
        pdf.cell(200, 5, txt=f"NIT: {nit_cliente}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Costo", 1)
        pdf.cell(40, 10, "Total", 1)
        pdf.ln()

        pdf.set_font("Arial", '', 10)
        for fila in datos:
            _, _, producto, cantidad, costo = fila
            total = float(cantidad) * float(costo)
            pdf.cell(60, 10, str(producto), 1)
            pdf.cell(30, 10, str(cantidad), 1)
            pdf.cell(30, 10, f"{costo:.2f}", 1)
            pdf.cell(40, 10, f"{total:.2f}", 1)
            pdf.ln()

        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=reporte_compras.pdf'
        return response
    except Exception as e:
        print(f"Error al generar el reporte PDF: {e}")
        return "Error al generar el reporte PDF", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        user = request.form['txtusuario']
        clave = request.form['txtclave']
        try:
            cursor = conexion.cursor()
            sql = 'SELECT * FROM tbusuario WHERE user=%s AND clave=%s'
            cursor.execute(sql, (user, hashlib.sha256(clave.encode()).hexdigest()))
            usuario = cursor.fetchone()
            cursor.close()

            if usuario:
                session['usuario'] = usuario[1]
                session['clave'] = usuario[3]
                return redirect('/')
            else:
                mensaje = "Usuario o contraseña incorrecto"
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            mensaje = "Error al iniciar sesión"
    return render_template('login.html', mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)