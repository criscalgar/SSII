import socket
import mysql.connector
import bcrypt
import hmac
import os
import hashlib

# Función para conectar a la base de datos
def conectar_base_datos():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="mi_base_datos",
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

# Verificar si el usuario existe
def verificar_usuario(nombre_usuario, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE LOWER(nombre_usuario) = %s", (nombre_usuario.lower(),))
    return cursor.fetchone()

# Registrar un nuevo usuario
def registrar_usuario(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO usuarios (nombre_usuario, clave) VALUES (%s, %s)", 
                   (nombre_usuario.lower(), hashed_password))
    db_conn.commit()
    return cursor.lastrowid

# Verificar la contraseña del usuario
def verificar_contraseña(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT clave FROM usuarios WHERE LOWER(nombre_usuario) = %s", 
                   (nombre_usuario.lower(),))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(clave.encode('utf-8'), result[0].encode('utf-8')):
        return True
    return False

# Registrar la transacción en la base de datos
def registrar_transaccion(emisor_nombre, destinatario_nombre, cantidad, db_conn):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO transacciones (emisor_nombre, destinatario_nombre, cantidad) VALUES (%s, %s, %s)", 
        (emisor_nombre, destinatario_nombre, cantidad)
    )
    db_conn.commit()
    return cursor.lastrowid

# Generar NONCE
def generar_nonce():
    return os.urandom(16)  # 16 bytes de NONCE

# Generar MAC
def generar_mac(key, message):
    return hmac.new(key, message.encode('utf-8'), hashlib.sha256).hexdigest()

# Verificar MAC
def verificar_mac(key, message, received_mac):
    return hmac.compare_digest(generar_mac(key, message), received_mac)

# Configuración del servidor
HOST = "127.0.0.1"
PORT = 8080
KEY = b'mi_clave_secreta_32_bytes_long'  # Clave secreta para el MAC

# Iniciar el servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Conectado por {addr}")

            db_conn = conectar_base_datos()
            try:
                while True:
                    # Recibir datos del cliente
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    # Extraer NONCE y MAC
                    nonce, received_mac, *message_parts = data.decode('utf-8').split(',')
                    message = ','.join(message_parts)

                    # Verificar el MAC
                    if not verificar_mac(KEY, message + nonce, received_mac):
                        respuesta = "Error: MAC inválido. Posible ataque de repetición."
                        conn.sendall(respuesta.encode('utf-8'))
                        continue

                    # Procesar el mensaje
                    datos = message.split(',')
                    if len(datos) >= 3:
                        accion = datos[0].lower()
                        nombre_usuario = datos[1].lower()
                        clave = datos[2]

                        if accion == "registrar":
                            if not verificar_usuario(nombre_usuario, db_conn):
                                usuario_id = registrar_usuario(nombre_usuario, clave, db_conn)
                                respuesta = f"Usuario '{nombre_usuario}' registrado exitosamente."
                            else:
                                respuesta = "El usuario ya existe."

                        elif accion == "iniciar":
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

                            cantidad = float(conn.recv(1024).decode('utf-8'))
                            if cantidad <= 0:
                                respuesta = "Error: La cantidad debe ser mayor que cero."
                                conn.sendall(respuesta.encode('utf-8'))
                                continue

                            transaccion_id = registrar_transaccion(nombre_usuario, destinatario, cantidad, db_conn)
                            respuesta = f"Transferencia #{transaccion_id} registrada exitosamente."
                            conn.sendall(respuesta.encode('utf-8'))

            except Exception as e:
                print(f"Ocurrió un error: {e}")
            finally:
                db_conn.close()