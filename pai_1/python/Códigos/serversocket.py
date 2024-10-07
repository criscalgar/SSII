import socket
import mysql.connector
import hmac
import hashlib
import bcrypt
import time
import os

SECRET_KEY = b"clave_super_secreta"

# Función para obtener la ruta del archivo log, organizado por carpeta de mes y día
def obtener_archivo_log(fallo=False):
    fecha_actual = time.localtime()
    carpeta_base = "Transacciones"  # Carpeta base llamada "Transacciones"
    carpeta_mes = time.strftime("%Y-%m", fecha_actual)  # Carpeta con formato Año-Mes (e.g., 2024-10)
    
    # Si es un fallo, se guarda en la carpeta "Fallos" dentro de la carpeta del mes
    if fallo:
        carpeta_mes = os.path.join(carpeta_base, carpeta_mes, "Fallos")
    else:
        carpeta_mes = os.path.join(carpeta_base, carpeta_mes)
    
    nombre_archivo = time.strftime("%d.log", fecha_actual)  # Archivo con formato Día (e.g., 15.log)

    # Crear la ruta completa
    if not os.path.exists(carpeta_mes):
        os.makedirs(carpeta_mes)  # Crear carpetas si no existen
    
    return os.path.join(carpeta_mes, nombre_archivo)

# Función para registrar en el log
def registrar_en_log(mensaje, fallo=False):
    archivo_log = obtener_archivo_log(fallo)  # Obtener el archivo log adecuado (fallo o éxito)
    with open(archivo_log, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensaje}\n")

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
        registrar_en_log(f"Error al conectar a la base de datos: {err}", fallo=True)
        return None

def verificar_usuario(nombre_usuario, db_conn):
    cursor = db_conn.cursor()
    nombre_usuario = nombre_usuario.lower()
    cursor.execute("SELECT id FROM usuarios WHERE LOWER(nombre_usuario) = %s", (nombre_usuario,))
    result = cursor.fetchone()

    if result:
        print(f"Usuario encontrado: {nombre_usuario} con ID {result[0]}")
    else:
        print(f"Usuario '{nombre_usuario}' no encontrado en la base de datos.")

    return result

def registrar_usuario(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO usuarios (nombre_usuario, clave) VALUES (%s, %s)", 
                   (nombre_usuario.lower(), hashed_password))
    db_conn.commit()
    registrar_en_log(f"Usuario '{nombre_usuario}' registrado exitosamente.")
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
    transaccion_id = cursor.lastrowid
    registrar_en_log(f"Transferencia #{transaccion_id} de {emisor_nombre} a {destinatario_nombre} por {cantidad} registrada.")
    return transaccion_id

def verificar_mac(mensaje, mac, nonce, nonce_list):
    mac_calculado = hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Verificar si el mensaje ha sido alterado (MITM)
    if mac != mac_calculado:
        registrar_en_log("Error: MAC no coincide, mensaje alterado (posible ataque MITM).", fallo=True)
        return False
    
    # Verificar si el nonce ya ha sido utilizado (replay attack)
    if nonce in nonce_list:
        registrar_en_log("Error: Nonce repetido, posible ataque de repetición (replay).", fallo=True)
        return False

    nonce_list.append(nonce)
    return True

# Configuración del servidor
HOST = "127.0.0.1"
PORT = 8080
nonce_list = []  # Lista para almacenar los nonces utilizados

db_conn = conectar_base_datos()
if not db_conn:
    exit(1)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}...")
        registrar_en_log(f"Servidor iniciado en {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Conectado por {addr}")
                registrar_en_log(f"Conexión establecida con {addr}")

                while True:
                    data = conn.recv(1024)
                    if not data:
                        print("Desconectado por el cliente.")
                        break

                    # Decodificar los datos recibidos
                    datos = data.decode('utf-8').split(',')
                    if len(datos) >= 5:
                        accion = datos[0]
                        nombre_usuario = datos[1].lower()
                        clave = datos[2]
                        nonce = datos[3]
                        mac = datos[4]

                        mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"
                        
                        # Comprobar integridad y prevención de ataques
                        if not verificar_mac(mensaje, mac, nonce, nonce_list):
                            respuesta = "Error: Mensaje modificado o nonce reutilizado."
                            conn.sendall(respuesta.encode('utf-8'))
                            continue

                        # Acciones para registrar e iniciar sesión
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

                        # Si la identidad es verificada, proceder con la transacción
                        if 'Identidad verificada' in respuesta:
                            destinatario = conn.recv(1024).decode('utf-8').lower()
                            print(f"Buscando destinatario: {destinatario}")  # Mensaje de depuración
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
                                registrar_en_log("Error en la cantidad ingresada durante la transacción.", fallo=True)
                                conn.sendall(respuesta.encode('utf-8'))
                    else:
                        print("Error: Datos recibidos en un formato inesperado.")
except Exception as e:
    print(f"Error durante la ejecución: {e}")
    registrar_en_log(f"Error durante la ejecución: {e}", fallo=True)
finally:
    db_conn.close()
    registrar_en_log("Conexión a la base de datos cerrada.")
