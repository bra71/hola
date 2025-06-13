import mysql.connector

conexion=mysql.connector.connect(
    host="bx9uq8dggt8mgety3slm-mysql.services.clever-cloud.com",
    user="uwa6xd7dhdumvzyr",
    password="7MrAdoGSvjAwr5zNLoKI",
    database="bx9uq8dggt8mgety3slm"
)
cursor=conexion.cursor()

print(conexion.is_connected())