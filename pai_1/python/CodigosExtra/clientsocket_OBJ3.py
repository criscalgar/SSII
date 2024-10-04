import socket
import os
import hmac
import hashlib

# Configuración del cliente
HOST = "127.0.0.1"
PORT = 8080
KEY = b'mi_clave_secreta_32_bytes_long'  # Clave secreta para el MAC

def generar_nonce():
    return os.urandom(16).hex()  # 16 bytes de NONCE en formato hexadecimal

def generar_mac(key, message):
    return hmac.new(key, message.encode('utf-8'), hashlib.sha256).hexdigest()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Pedir al usuario que elija una acción
    accion = input("Ingrese:\n\n-'Registrar' para crear un nuevo usuario\n-'Iniciar' para iniciar sesión\n\nAcción a realizar: ")

    # Verificar que la acción sea válida
    if accion.lower() not in ['registrar', 'iniciar']:
        print("\nAcción inválida. Desconectando...")
        s.close()
        exit()

    # Pedir al usuario que ingrese sus datos
    nombre_usuario = input("\nIngrese el nombre de usuario (nombre y apellidos): ")
    clave = input("\nIngrese la clave: ")

    # Generar NONCE
    nonce = generar_nonce()  # Generar NONCE
    mensaje = f"{accion},{nombre_usuario.lower()},{clave}"
    
    # Generar MAC
    mac = generar_mac(KEY, mensaje)

    # Formatear los datos en una cadena
    datos = f"{nonce},{mac},{mensaje}"
    s.sendall(datos.encode('utf-8'))

    # Recibir la respuesta del servidor
    respuesta = s.recv(1024).decode('utf-8')
    print(f"\n{respuesta}")

    if "Identidad verificada" in respuesta:
        # Pedir al usuario el nombre del destinatario
        destinatario = input("\nIngrese el nombre del destinatario (nombre y apellidos): ")
        destinatario = destinatario.lower()
        s.sendall(destinatario.encode('utf-8'))

        # Recibir respuesta sobre la verificación del destinatario
        respuesta = s.recv(1024).decode('utf-8')
        print(f"\n{respuesta}")

        if "verificado" in respuesta:
            cantidad = input("\nIngrese la cantidad a transferir: ")
            s.sendall(cantidad.encode('utf-8'))

            respuesta = s.recv(1024).decode('utf-8')
            print(f"\n{respuesta}")