import socket
import hmac
import hashlib
import time
import os

# Clave secreta compartida entre cliente y servidor
SECRET_KEY = b"clave_super_secreta"

# Función para generar un nonce único
def generar_nonce():
    return str(int(time.time())) + str(os.getpid())

# Función para generar MAC usando HMAC-SHA256
def generar_mac(mensaje):
    return hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()

# Configuración del cliente
HOST = "127.0.0.1"
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Pedir al usuario que elija una acción
    accion = input("Ingrese:\n\n-'Registrar' para crear un nuevo usuario\n-'Iniciar' para iniciar sesión\nAccion a realizar: ")

    # Pedir al usuario que ingrese sus datos
    nombre_usuario = input("Ingrese el nombre de usuario: ")
    clave = input("Ingrese la clave: ")

    # Generar un nonce único para la transacción
    nonce = generar_nonce()

    # Formatear los datos en una cadena
    mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"
    
    # Generar el MAC del mensaje
    mac = generar_mac(mensaje)

    # Enviar los datos junto con el nonce y el MAC al servidor
    datos = f"{mensaje},{mac}"
    s.sendall(datos.encode('utf-8'))
    
    # Recibir la respuesta del servidor
    respuesta = s.recv(1024).decode('utf-8')
    print(f"Respuesta del servidor: {respuesta}")

    if "Identidad verificada" in respuesta:
        cantidad = input("Ingrese la cantidad a transferir: ")
        s.sendall(cantidad.encode('utf-8'))

        respuesta = s.recv(1024).decode('utf-8')
        print(f"Respuesta del servidor: {respuesta}")