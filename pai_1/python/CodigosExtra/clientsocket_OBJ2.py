import socket

# Configuración del cliente
HOST = "127.0.0.1"
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Pedir al usuario que elija una acción
    accion = input("Ingrese:\n\n-'Registrar' para crear un nuevo usuario\n-'Iniciar' para iniciar sesion\n\nAccion a realizar: ")

    # Verificar que la acción sea válida
    if accion.lower() not in ['registrar', 'iniciar']:
        print("\nAccion invalida. Desconectando...")
        s.close()  # Cerrar la conexión
        exit()  # Salir del programa

    # Pedir al usuario que ingrese sus datos
    nombre_usuario = input("\nIngrese el nombre de usuario (nombre y apellidos): ")
    clave = input("\nIngrese la clave: ")

    nombre_usuario = nombre_usuario.lower()

    # Formatear los datos en una cadena
    mensaje = f"{accion},{nombre_usuario},{clave}"

    datos = f"{mensaje}"
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