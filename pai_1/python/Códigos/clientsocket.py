import socket
import hmac
import hashlib
import time
import os

SECRET_KEY = b"clave_super_secreta"

def generar_nonce():
    return str(int(time.time())) + str(os.getpid())

def generar_mac(mensaje):
    return hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()

HOST = "127.0.0.1"
PORT = 8080

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Pedir al usuario que elija una acción
        accion = input("Ingrese:\n\n-'Registrar' para crear un nuevo usuario\n-'Iniciar' para iniciar sesión\n\nAcción a realizar: ").strip().lower()

        if accion not in ['registrar', 'iniciar']:
            print("\nAcción inválida. Desconectando...")
            exit()

        # Pedir al usuario que ingrese sus datos
        nombre_usuario = input("\nIngrese el nombre de usuario (nombre y apellidos): ").strip()
        clave = input("\nIngrese la clave: ").strip()

        nombre_usuario = nombre_usuario.lower()

        nonce = generar_nonce()
        mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"
        
        mac = generar_mac(mensaje)
        datos = f"{mensaje},{mac}"
        s.sendall(datos.encode('utf-8'))
        
        respuesta = s.recv(1024).decode('utf-8')
        print(f"\n{respuesta}")

        if "Identidad verificada" in respuesta:
            destinatario = input("\nIngrese el nombre del destinatario (nombre y apellidos): ").strip().lower()
            s.sendall(destinatario.encode('utf-8'))

            respuesta = s.recv(1024).decode('utf-8')
            print(f"\n{respuesta}")

            if "verificado" in respuesta:
                try:
                    cantidad = float(input("\nIngrese la cantidad a transferir: "))
                    s.sendall(str(cantidad).encode('utf-8'))

                    respuesta = s.recv(1024).decode('utf-8')
                    print(f"\n{respuesta}")
                except ValueError:
                    print("Error: La cantidad ingresada no es válida.")
except Exception as e:
    print(f"Error de conexión: {e}")