import socket
import hmac
import hashlib
import time
import os

SECRET_KEY = b"clave_super_secreta"
LOG_FILE = "registro_pruebas.log"

def generar_nonce():
    return str(int(time.time())) + str(os.getpid())

def generar_mac(mensaje):
    return hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()

def enviar_transaccion(accion, nombre_usuario, clave, destinatario, cantidad):
    HOST = "127.0.0.1"  
    PORT = 8080         

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))

            # Crear mensaje
            nonce = generar_nonce()
            mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"
            mac = generar_mac(mensaje)
            datos = f"{mensaje},{mac}"

            # Enviar datos al servidor
            s.sendall(datos.encode('utf-8'))

            # Recibir respuesta del servidor
            respuesta = s.recv(1024).decode('utf-8')
            print(f"Respuesta del servidor: {respuesta}")

            if "Identidad verificada" in respuesta:
                # Enviar el destinatario
                s.sendall(destinatario.encode('utf-8'))

                # Recibir la respuesta sobre la cantidad
                respuesta = s.recv(1024).decode('utf-8')
                print(f"Respuesta del servidor: {respuesta}")

                if "Ingrese la cantidad a transferir" in respuesta:
                    s.sendall(str(cantidad).encode('utf-8'))

                    # Recibir la respuesta final
                    respuesta = s.recv(1024).decode('utf-8')
                    print(f"Respuesta del servidor: {respuesta}")

    except ConnectionRefusedError:
        print("Error: No se pudo conectar al servidor. Asegúrate de que esté en ejecución.")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Función para registrar el mensaje en el archivo de log
def registrar_log(mensaje):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(mensaje + "\n")

def realizar_pruebas(num_pruebas):
    
    accion = "iniciar"  # O "registrar" dependiendo de tu prueba
    nombre_usuario = "blanca garcia alonso"  # Cambia esto si es necesario
    clave = "123456"  # Cambia esto si es necesario
    destinatario = "cristina calderon garcia"  # Asegúrate de que este usuario esté registrado
    cantidad = 100.0  # Ajusta según sea necesario

    # Realizar las pruebas una sola vez
    inicio = time.time()
    for _ in range(num_pruebas):
        enviar_transaccion(accion, nombre_usuario, clave, destinatario, cantidad)
        time.sleep(0.5)  # Retraso para evitar sobrecarga
    tiempo_transcurrido = time.time() - inicio
    mensaje = f"Se completaron {num_pruebas} pruebas en {tiempo_transcurrido:.2f} segundos."
    
    print(mensaje)
    registrar_log(mensaje)  # Registrar el mensaje en el archivo de log

    time.sleep(2)  # Retraso opcional antes de la siguiente serie de pruebas

# Realizar pruebas automáticas
if __name__ == "__main__":
    realizar_pruebas(5)     # Bucle para 5 pruebas
    realizar_pruebas(50)    # Bucle para 50 pruebas
    realizar_pruebas(500)   # Bucle para 500 pruebas

