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

    conn, addr = s.accept()
    try:
        print(f"\nConectado por {addr}")

        # Recibe nombre de usuario y contraseña
        datos = conn.recv(1024).decode('utf-8').split(',')
        if len(datos) != 2:
            conn.sendall(b"\nFormato incorrecto")
        else:
            nombre_usuario, contraseña = datos
            if autenticar_usuario(nombre_usuario, contraseña):
                conn.sendall(b"\nAutenticacion exitosa")
                print(f"\nUsuario autenticado: {nombre_usuario}")

                # Después de la autenticación, el servidor espera recibir mensajes de transferencia
                cantidad = conn.recv(1024).decode('utf-8')
                if cantidad:
                    # Procesar la cantidad según sea necesario
                    print(f"\nTransferencia recibida de {nombre_usuario}: - Cantidad: {cantidad}")
                    conn.sendall(b"\nTransferencia recibida")

                print("\nCerrando conexión después de la transferencia.")
            else:
                conn.sendall(b"\nAutenticacion fallida")
                print("\nAutenticación fallida. Cerrando conexión.")

    except Exception as e:
        print(f"\nError durante la conexión con {addr}: {e}")

    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)  # Cerrar envíos y recepciones
        except OSError:
            pass  # Ignorar si la conexión ya está cerrada
        finally:
            conn.close()  # Cerrar el socket correctamente
            print(f"\nConexión cerrada con {addr}")

print("\nServidor cerrado.")