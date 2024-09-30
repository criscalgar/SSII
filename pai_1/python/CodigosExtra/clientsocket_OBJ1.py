import socket

HOST = "127.0.0.1"  # La dirección del servidor
PORT = 3030  # El puerto que usa el servidor

# Datos del usuario (nombre y contraseña)
nombre_usuario = input("Nombre de usuario: ")
contraseña = input("\nClave: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # Enviar nombre de usuario y contraseña al servidor
    mensaje_autenticacion = f"{nombre_usuario},{contraseña}"
    s.sendall(mensaje_autenticacion.encode('utf-8'))
    
    # Recibir respuesta del servidor
    respuesta = s.recv(1024).decode('utf-8')
    print(respuesta)

    if "Autenticacion exitosa" in respuesta:
        # Una vez autenticado, el cliente puede enviar mensajes de transferencia
        cantidad = input("\nEscribe la cantidad a transferir: ")
        
        # Enviar la cantidad al servidor
        s.sendall(cantidad.encode('utf-8'))
        
        # Recibir confirmación del servidor
        confirmacion = s.recv(1024).decode('utf-8')
        print(confirmacion)

    # Cerrar la conexión
    print("\nCerrando conexión.")