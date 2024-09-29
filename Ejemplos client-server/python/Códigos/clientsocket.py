import socket

HOST = "127.0.0.1"  # La dirección IP del servidor
PORT = 8080  # El puerto en el que el servidor está escuchando

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Pedir al usuario que ingrese sus datos
    nombre_usuario = input("Ingrese el nombre de usuario: ")
    clave = input("Ingrese la clave: ")

    # Formatear los datos en una cadena separada por comas
    datos = f"{nombre_usuario},{clave}"
    
    # Enviar los datos al servidor
    s.sendall(datos.encode('utf-8'))
    
    # Recibir la respuesta del servidor
    respuesta = s.recv(1024).decode('utf-8')
    print(f"Respuesta del servidor: {respuesta}")

    # Verificar si la identidad fue verificada
    if "Identidad verificada" in respuesta:
        cantidad = input("Ingrese la cantidad a transferir: ")
        # Enviar la cantidad al servidor
        s.sendall(cantidad.encode('utf-8'))

        # Recibir la respuesta de la transacción
        respuesta = s.recv(1024).decode('utf-8')
        print(f"Respuesta del servidor: {respuesta}")