import socket
import mysql.connector

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
def registrar_transaccion(usuario_id, cantidad, db_conn):
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO transacciones (usuario_id, cantidad) VALUES (%s, %s)", 
        (usuario_id, cantidad)
    )
    db_conn.commit()
    return cursor.lastrowid

# Configuración del servidor
HOST = "127.0.0.1"
PORT = 8080

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

            # Datos recibidos: acción, nombre_usuario, clave (si aplica)
            datos = data.decode('utf-8').split(',')
            if len(datos) >= 2:
                accion = datos[0]
                nombre_usuario = datos[1]
                clave = datos[2] if len(datos) == 3 else None

                if accion == "registrar" or accion == "Registrar" or accion == "REGISTRAR":
                    if not verificar_usuario(nombre_usuario, db_conn):
                        usuario_id = registrar_usuario(nombre_usuario, clave, db_conn)
                        respuesta = f"Usuario '{nombre_usuario}' registrado exitosamente."
                    else:
                        respuesta = "El usuario ya existe."

                elif accion == "iniciar" or accion == "Iniciar" or accion == "INICIAR":
                    usuario_info = verificar_contraseña(nombre_usuario, clave, db_conn)
                    if usuario_info:
                        usuario_id = usuario_info[0]
                        respuesta = "Identidad verificada. Por favor, envie la cantidad a transferir."
                    else:
                        respuesta = "Usuario o clave incorrectos."

                else:
                    respuesta = "Accion no reconocida."

                # Enviar respuesta al cliente
                conn.sendall(respuesta.encode('utf-8'))

                # Esperar la cantidad a transferir solo si la identidad es verificada
                if 'Identidad verificada' in respuesta:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    cantidad = float(data.decode('utf-8'))
                    
                    # Registrar la transacción
                    transaccion_id = registrar_transaccion(usuario_id, cantidad, db_conn)
                    respuesta = f"Transferencia #{transaccion_id} registrada exitosamente."
                    conn.sendall(respuesta.encode('utf-8'))

        # Cerrar la conexión a la base de datos
        db_conn.close()