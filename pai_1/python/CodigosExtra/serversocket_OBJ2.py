import socket
import mysql.connector
import bcrypt  # Importar bcrypt para el hashing de contraseñas


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
    nombre_usuario = nombre_usuario.lower()  # Convertir a minúsculas
    cursor.execute("SELECT id FROM usuarios WHERE LOWER(nombre_usuario) = %s", (nombre_usuario,))
    return cursor.fetchone()

# Registrar un nuevo usuario
def registrar_usuario(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt())  # Hashear la clave
    cursor.execute("INSERT INTO usuarios (nombre_usuario, clave) VALUES (%s, %s)", 
                   (nombre_usuario.lower(), hashed_password))  # Guardar en minúsculas
    db_conn.commit()
    return cursor.lastrowid

def registrar_usuarios_por_defecto(db_conn):
    usuarios = [
        ("yassine nacif", "123456"),
        ("blanca garcia alonso", "123456"),
        ("cristina calderon garcia", "123456")
    ]
    
    for nombre_usuario, clave in usuarios:
        if not verificar_usuario(nombre_usuario, db_conn):
            registrar_usuario(nombre_usuario, clave, db_conn)
            print(f"Usuario '{nombre_usuario}' registrado exitosamente.")
        else:
            print(f"El usuario '{nombre_usuario}' ya existe.")

# Verificar la contraseña del usuario
def verificar_contraseña(nombre_usuario, clave, db_conn):
    cursor = db_conn.cursor()
    nombre_usuario = nombre_usuario.lower()  # Convertir a minúsculas
    cursor.execute("SELECT clave FROM usuarios WHERE LOWER(nombre_usuario) = %s", 
                   (nombre_usuario,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(clave.encode('utf-8'), result[0].encode('utf-8')):  # Verificar la clave hasheada
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
        # Registrar usuarios por defecto
        registrar_usuarios_por_defecto(db_conn)
        
        while True:
            # Recibir datos del cliente
            data = conn.recv(1024)
            if not data:
                break

            # Datos recibidos: accion, nombre_usuario, clave
            datos = data.decode('utf-8').split(',')
            if len(datos) >= 3:
                accion = datos[0]
                nombre_usuario = datos[1].lower()  # Convertir a minúsculas
                clave = datos[2]

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
                    respuesta = "Accion no reconocida."

                # Enviar respuesta al cliente
                conn.sendall(respuesta.encode('utf-8'))

                if 'Identidad verificada' in respuesta:
                    destinatario = conn.recv(1024).decode('utf-8').lower()  # Convertir a minúsculas
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