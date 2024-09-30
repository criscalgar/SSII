import socket
import mysql.connector
import hmac
import hashlib
import time
import os

# Clave secreta compartida entre cliente y servidor
SECRET_KEY = b"clave_super_secreta"

# Función para conectar a la base de datos
def conectar_base_datos():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="pai_1",
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

# Verificar si el usuario existe
def verificar_usuario(nombre_usuario, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
    return cursor.fetchone()

# Registrar un nuevo usuario
def registrar_usuario(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre_usuario, clave) VALUES (%s, %s)", 
                   (nombre_usuario, clave))
    db_conn.commit()
    return cursor.lastrowid

# Verificar la contraseña del usuario
def verificar_contraseña(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s AND clave = %s", 
                   (nombre_usuario, clave))
    return cursor.fetchone()

# Registrar la transacción en la base de datos
def registrar_transaccion(emisor_nombre, destinatario_nombre, cantidad, db_conn):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO transacciones (emisor_nombre, destinatario_nombre, cantidad) VALUES (%s, %s, %s)", 
        (emisor_nombre, destinatario_nombre, cantidad)
    )
    db_conn.commit()
    return cursor.lastrowid

# Función para verificar MAC y nonce
def verificar_mac(mensaje, mac, nonce, nonce_list):
    mac_calculado = hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()
    if mac != mac_calculado:
        return False
    if nonce in nonce_list:
        return False  # Replay attack detectado
    nonce_list.append(nonce)
    return True

# Configuración del servidor
HOST = "127.0.0.1"
PORT = 8080
nonce_list = []  # Lista para almacenar nonces usados

# Iniciar el servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}...")

    conn, addr = s.accept()
    with conn:
        print(f"Conectado por {addr}")

        db_conn = conectar_base_datos()

        while True:
            # Recibir datos del cliente
            data = conn.recv(1024)
            if not data:
                break

            # Datos recibidos: accion, nombre_usuario, clave, nonce, mac
            datos = data.decode('utf-8').split(',')
            if len(datos) >= 5:
                accion = datos[0]
                nombre_usuario = datos[1]
                clave = datos[2]
                nonce = datos[3]
                mac = datos[4]

                # Verificar la integridad del mensaje con el MAC y el nonce
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
                    usuario_info = verificar_contraseña(nombre_usuario, clave, db_conn)
                    if usuario_info:
                        respuesta = "Identidad verificada. Por favor, indique el nombre del destinatario."
                    else:
                        respuesta = "Usuario o clave incorrectos."

                else:
                    respuesta = "Accion no reconocida."

                # Enviar respuesta al cliente
                conn.sendall(respuesta.encode('utf-8'))

                if 'Identidad verificada' in respuesta:
                    destinatario = conn.recv(1024).decode('utf-8')
                    if not verificar_usuario(destinatario, db_conn):
                        respuesta = "Error: El usuario destinatario no existe."
                        conn.sendall(respuesta.encode('utf-8'))
                        continue
                    
                    respuesta = "Usuario destinatario verificado. Ingrese la cantidad a transferir."
                    conn.sendall(respuesta.encode('utf-8'))

                    cantidad = float(conn.recv(1024).decode('utf-8'))
                    
                    # Registrar la transacción
                    transaccion_id = registrar_transaccion(nombre_usuario, destinatario, cantidad, db_conn)
                    respuesta = f"Transferencia #{transaccion_id} registrada exitosamente."
                    conn.sendall(respuesta.encode('utf-8'))

        db_conn.close()