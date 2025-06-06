import mysql.connector

conexion=mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="db_ventas"
)
cursor=conexion.cursor()

print(conexion.is_connected())