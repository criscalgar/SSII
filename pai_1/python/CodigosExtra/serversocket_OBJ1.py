import socket
import bcrypt

# Usuarios predefinidos con contraseñas hashadas
usuarios = {
    "cristina": bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()),
    "blanca": bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()),
    "yassif": bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())
}

def autenticar_usuario(nombre_usuario, contraseña):
    nombre_usuario = nombre_usuario.lower()  # Insensibilidad a mayúsculas/minúsculas
    if nombre_usuario in usuarios:
        return bcrypt.checkpw(contraseña.encode('utf-8'), usuarios[nombre_usuario])
    return False

HOST = "127.0.0.1"
PORT = 3030

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("\nServidor escuchando en", HOST, ":", PORT)
    
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\nConectado por {addr}")
            
            # Recibe nombre de usuario y contraseña
            datos = conn.recv(1024).decode('utf-8').split(',')
            if len(datos) != 2:
                conn.sendall(b"\nFormato incorrecto")
                continue

            nombre_usuario, contraseña = datos
            if autenticar_usuario(nombre_usuario, contraseña):
                conn.sendall(b"\nAutenticacion exitosa")
                print(f"\nUsuario autenticado: {nombre_usuario}")
                
                # Después de la autenticación, el servidor espera recibir mensajes de transferencia
                while True:
                    # Esperar a que el cliente envíe la cantidad
                    cantidad = conn.recv(1024).decode('utf-8')
                    if not cantidad:
                        print("\nConexión cerrada por el cliente.")
                        break
                    
                    # Procesar la cantidad según sea necesario
                    print(f"\nTransferencia recibida de {nombre_usuario}: - Cantidad: {cantidad}")
                    conn.sendall(b"\nTransferencia recibida")
                
                print("\nCerrando conexión después de la transferencia.")
            else:
                conn.sendall(b"\nAutenticacion fallida")
                print("\nAutenticación fallida. Cerrando conexión.")