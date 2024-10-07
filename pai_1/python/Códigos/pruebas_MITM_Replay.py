import socket
import hmac
import hashlib
import time
import os
import random
from datetime import datetime

SECRET_KEY = b"clave_super_secreta"

fallos_mitm = 0
fallos_replay = 0

# Función para generar un nonce
def generar_nonce():
    return str(int(time.time())) + str(os.getpid())

# Función para generar un HMAC
def generar_mac(mensaje):
    return hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()

# Función para obtener la ruta del archivo log para transacciones
def obtener_ruta_log_fallos():
    fecha_actual = datetime.now()
    carpeta_base = "Fallos"  # Carpeta base para fallos
    carpeta_mes = fecha_actual.strftime("%Y-%m")  # Carpeta con formato Año-Mes
    nombre_archivo = f"{fecha_actual.strftime('%d')}.log"  # Archivo con formato Día
    
    ruta_carpeta = os.path.join(carpeta_base, carpeta_mes)
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)
    
    return os.path.join(ruta_carpeta, nombre_archivo)

# Función para obtener la ruta del archivo log para tiempos
def obtener_ruta_log_tiempos():
    fecha_actual = datetime.now()
    carpeta_base = "Tiempos"  # Carpeta base para tiempos
    carpeta_mes = fecha_actual.strftime("%Y-%m")  # Carpeta con formato Año-Mes
    nombre_archivo = f"{fecha_actual.strftime('%d')}_tiempos.log"  # Archivo con formato Día
    
    ruta_carpeta = os.path.join(carpeta_base, carpeta_mes)
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)
    
    return os.path.join(ruta_carpeta, nombre_archivo)

# Función para registrar los fallos en el archivo de log
def registrar_mensaje(mensaje):
    ruta_log = obtener_ruta_log_fallos()
    with open(ruta_log, "a") as f:
        f.write(mensaje + "\n")

# Función para registrar los tiempos en el archivo de log
def registrar_tiempo(mensaje):
    ruta_log = obtener_ruta_log_tiempos()
    with open(ruta_log, "a") as f:
        f.write(mensaje + "\n")

# Función para realizar transacciones reales
# Función para realizar transacciones reales
def enviar_transaccion(accion, nombre_usuario, clave, destinatario, cantidad, modificar=False, replay=False):
    HOST = "127.0.0.1"
    PORT = 8080

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))

            # Crear el mensaje original
            nonce = generar_nonce()
            mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"
            mac = generar_mac(mensaje)
            datos = f"{mensaje},{mac}"

            if modificar:
                # Simular un ataque MITM modificando el mensaje
                # Aquí se modifica el mensaje original (por ejemplo, cambiando el destinatario)
                mensaje_modificado = f"{accion},{nombre_usuario},{clave},{nonce},MODIFICADO"  # Cambio en el mensaje
                mac_modificado = generar_mac(mensaje_modificado)  # Se recalcula el MAC del mensaje modificado
                datos = f"{mensaje_modificado},{mac_modificado}"  # Enviar el mensaje modificado y su MAC incorrecto

            if replay:
                # Simular un replay atacando el mismo mensaje varias veces
                pass  # Replay es enviar el mismo mensaje más de una vez

            # Enviar el mensaje al servidor
            s.sendall(datos.encode('utf-8'))

            # Recibir la respuesta del servidor
            respuesta = s.recv(1024).decode('utf-8')
            print(f"Respuesta del servidor: {respuesta}")
            registrar_mensaje(f"Dia {datetime.now().day} {datetime.now().strftime('%H:%M')}: {respuesta}")

            # Si la identidad es verificada, continuar con la transacción
            if "Identidad verificada" in respuesta:
                # Enviar el destinatario
                s.sendall(destinatario.encode('utf-8'))

                # Recibir respuesta sobre la cantidad
                respuesta = s.recv(1024).decode('utf-8')
                print(f"Respuesta del servidor: {respuesta}")
                registrar_mensaje(f"Dia {datetime.now().day} {datetime.now().strftime('%H:%M')}: {respuesta}")

                if "Ingrese la cantidad a transferir" in respuesta:

                    s.sendall(str(cantidad).encode('utf-8'))

                    # Recibir la respuesta final
                    respuesta = s.recv(1024).decode('utf-8')
                    print(f"Respuesta final del servidor: {respuesta}")
                    registrar_mensaje(f"Dia {datetime.now().day} {datetime.now().strftime('%H:%M')}: {respuesta}")

    except ConnectionRefusedError:
        print("Error: No se pudo conectar al servidor.")
        registrar_mensaje("Error: No se pudo conectar al servidor.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        registrar_mensaje(f"Error inesperado: {e}")


# Función para realizar pruebas MITM y Replay, y registrar los tiempos
def realizar_pruebas(num_pruebas):
    global fallos_mitm, fallos_replay
    
    accion = "iniciar"  # O "registrar"
    nombre_usuario = "cristina calderon garcia"
    clave = "123456"
    destinatario = "blanca garcia alonso"
    cantidad = 100.0

    inicio_tiempo = time.time()  # Registrar el tiempo de inicio

    for _ in range(num_pruebas):
        # Elegir aleatoriamente el tipo de prueba
        tipo_prueba = random.choice(["MITM", "REPLAY", "NORMAL"])
        
        if tipo_prueba == "MITM":
            enviar_transaccion(accion, nombre_usuario, clave, destinatario, cantidad, modificar=True)
            registrar_mensaje(f"Dia {datetime.now().day} {datetime.now().strftime('%H:%M')}: FALLO - Se intentó modificar un mensaje (MITM)")
            fallos_mitm += 1
        elif tipo_prueba == "REPLAY":
            enviar_transaccion(accion, nombre_usuario, clave, destinatario, cantidad, replay=True)
            registrar_mensaje(f"Dia {datetime.now().day} {datetime.now().strftime('%H:%M')}: FALLOREPLAY - Se intentó realizar un replay")
            fallos_replay += 1
        else:
            enviar_transaccion(accion, nombre_usuario, clave, destinatario, cantidad)
            registrar_mensaje(f"Dia {datetime.now().day} {datetime.now().strftime('%H:%M')}: ACIERTO - No se ha modificado ningún mensaje")

    fin_tiempo = time.time()  # Registrar el tiempo de finalización
    tiempo_total = fin_tiempo - inicio_tiempo
    registrar_tiempo(f"Bucle completado: {num_pruebas} pruebas realizadas en {tiempo_total:.2f} segundos.")

    # Registrar resumen de fallos
    registrar_mensaje(f"\nHan ocurrido un total de {fallos_mitm} fallos de Man-in-the-Middle")
    registrar_mensaje(f"Han ocurrido un total de {fallos_replay} fallos de Replay")

# Ejecutar las pruebas y registrar los tiempos
if __name__ == "__main__":
    realizar_pruebas(500)   # Realizar 500 pruebas
    realizar_pruebas(5000)  # Realizar 5000 pruebas
    realizar_pruebas(50000) # Realizar 50000 pruebas
