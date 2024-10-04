import socket
import mysql.connector
import hmac
import hashlib
import bcrypt
import time
import os

SECRET_KEY = b"clave_super_secreta"

def conectar_base_datos():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="pai_1",
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

def verificar_usuario(nombre_usuario, db_conn):
    cursor = db_conn.cursor()
    nombre_usuario = nombre_usuario.lower()
    cursor.execute("SELECT id FROM usuarios WHERE LOWER(nombre_usuario) = %s", (nombre_usuario,))
    return cursor.fetchone()

def registrar_usuario(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO usuarios (nombre_usuario, clave) VALUES (%s, %s)", 
                   (nombre_usuario.lower(), hashed_password))
    db_conn.commit()
    return cursor.lastrowid

def verificar_contraseña(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    nombre_usuario = nombre_usuario.lower()
    cursor.execute("SELECT clave FROM usuarios WHERE LOWER(nombre_usuario) = %s", 
                   (nombre_usuario,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(clave.encode('utf-8'), result[0].encode('utf-8')):
        return True
    return False

def registrar_transaccion(emisor_nombre, destinatario_nombre, cantidad, db_conn):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO transacciones (emisor_nombre, destinatario_nombre, cantidad) VALUES (%s, %s, %s)", 
        (emisor_nombre, destinatario_nombre, cantidad)
    )
    db_conn.commit()
    return cursor.lastrowid

def verificar_mac(mensaje, mac, nonce, nonce_list):
    mac_calculado = hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()
    if mac != mac_calculado:
        return False
    if nonce in nonce_list:
        return False
    nonce_list.append(nonce)
    return True

HOST = "127.0.0.1"
PORT = 8080
nonce_list = []

db_conn = conectar_base_datos()
if not db_conn:
    exit(1)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}...")

        conn, addr = s.accept()
        with conn:
            print(f"Conectado por {addr}")

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                datos = data.decode('utf-8').split(',')
                if len(datos) >= 5:
                    accion = datos[0]
                    nombre_usuario = datos[1].lower()
                    clave = datos[2]
                    nonce = datos[3]
                    mac = datos[4]

                    mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"
                    if not verificar_mac(mensaje, mac, nonce, nonce_list):
                        respuesta = "Error: Mensaje modificado o nonce reutilizado."
                        conn.sendall(respuesta.encode('utf-8'))
                        continue

                    if accion.lower() == "registrar":
                        if not verificar_usuario(nombre_usuario, db_conn):
                            usuario_id = registrar_usuario(nombre_usuario, clave, db_conn)
                            respuesta = f"Usuario '{nombre_usuario}' registrado exitosamente."
                        else:
                            respuesta = "El usuario ya existe."

                    elif accion.lower() == "iniciar":
                        if verificar_contraseña(nombre_usuario, clave, db_conn):
                            respuesta = "Identidad verificada. Por favor, indique el nombre del destinatario."
                        else:
                            respuesta = "Usuario o clave incorrectos."

                    else:
                        respuesta = "Acción no reconocida."

                    conn.sendall(respuesta.encode('utf-8'))

                    if 'Identidad verificada' in respuesta:
                        destinatario = conn.recv(1024).decode('utf-8').lower()
                        if not verificar_usuario(destinatario, db_conn):
                            respuesta = "Error: El usuario destinatario no existe."
                            conn.sendall(respuesta.encode('utf-8'))
                            continue
                        
                        respuesta = "Usuario destinatario verificado. Ingrese la cantidad a transferir."
                        conn.sendall(respuesta.encode('utf-8'))

                        try:
                            cantidad = float(conn.recv(1024).decode('utf-8'))
                            transaccion_id = registrar_transaccion(nombre_usuario, destinatario, cantidad, db_conn)
                            respuesta = f"Transferencia #{transaccion_id} registrada exitosamente."
                            conn.sendall(respuesta.encode('utf-8'))
                        except ValueError:
                            respuesta = "Error: La cantidad ingresada no es válida."
                            conn.sendall(respuesta.encode('utf-8'))
except Exception as e:
    print(f"Error durante la ejecución: {e}")
finally:
    db_conn.close()