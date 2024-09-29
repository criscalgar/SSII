Librerías Importadas

socket: Esta biblioteca es parte de la biblioteca estándar de Python y se utiliza para crear conexiones de red.
Permite la comunicación entre el cliente y el servidor mediante el uso de sockets, que son puntos finales para
el envío y recepción de datos.

hmac: HMAC (Hash-based Message Authentication Code) es un mecanismo que utiliza una función hash y una clave
secreta para proporcionar autenticación de mensajes. Se utiliza para asegurar la integridad y autenticidad de los
datos enviados entre el cliente y el servidor.

hashlib: Esta biblioteca proporciona una interfaz para varios algoritmos de hash, incluyendo SHA-256. Se utiliza
para generar un resumen (hash) de los datos, que es esencial para crear el MAC.

time: Se utiliza para obtener el tiempo actual, que se emplea en la generación de un nonce único. El nonce ayuda 
a prevenir ataques de repetición al garantizar que cada mensaje sea único.

os: Proporciona una manera de interactuar con el sistema operativo. Se utiliza aquí para obtener el ID del proceso
actual (os.getpid()), que se combina con el tiempo para generar un nonce único.


*Clave Secreta:*

SECRET_KEY = b"clave_super_secreta"

Se define una clave secreta compartida entre el cliente y el servidor. Esta clave se utiliza para generar el código
de autenticación del mensaje (MAC) y asegurar la integridad de los datos.

*Generación de Nonce:*

def generar_nonce():
    return str(int(time.time())) + str(os.getpid())

Esta función genera un nonce único combinando el tiempo actual (en segundos desde la época) con el ID del proceso.
Esto asegura que cada nonce sea diferente, incluso si se generan en rápida sucesión.

*Generación de MAC:*

def generar_mac(mensaje):
    return hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()

Esta función genera un MAC utilizando HMAC con el algoritmo SHA-256. Toma un mensaje (cadena de texto), lo codifica
en bytes y lo utiliza junto con la SECRET_KEY para crear un resumen hash. El resultado se devuelve como una cadena
hexadecimal.

*Configuración del Cliente:*

HOST = "127.0.0.1"
PORT = 8080

Aquí se especifica la dirección IP y el puerto al que se conectará el cliente. En este caso, se conecta al servidor
que está en la misma máquina (127.0.0.1 se refiere a localhost).

*Conexión al Servidor:*

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

Se crea un socket TCP y se conecta al servidor en la dirección y puerto especificados. La instrucción with asegura que
el socket se cierre adecuadamente al final del bloque.

*Interacción con el Usuario:*

accion = input("Ingrese:\n\n-'Registrar' para crear un nuevo usuario\n-'Iniciar' para iniciar sesión\nAccion a realizar: ")
nombre_usuario = input("Ingrese el nombre de usuario: ")
clave = input("Ingrese la clave: ")

Se le pide al usuario que elija una acción (Registrar o Iniciar) y que proporcione su nombre de usuario y contraseña.

*Generación del Nonce y Formateo del Mensaje:*

nonce = generar_nonce()
mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"

Se genera un nonce único y se crea un mensaje que contiene la acción, el nombre de usuario, la clave y el nonce. Este mensaje
se utilizará para la autenticación.

*Generación del MAC:*

mac = generar_mac(mensaje)

Se genera el MAC para el mensaje, lo que permite verificar su integridad y autenticidad más adelante.

*Envío de Datos al Servidor:*

datos = f"{mensaje},{mac}"
s.sendall(datos.encode('utf-8'))

Se combinan el mensaje y el MAC en una sola cadena, que se codifica en bytes y se envía al servidor. sendall garantiza que todos
los datos sean enviados.

*Recepción de la Respuesta del Servidor:*

respuesta = s.recv(1024).decode('utf-8')
print(f"Respuesta del servidor: {respuesta}")

El cliente espera y recibe una respuesta del servidor. recv(1024) indica que se recibirán hasta 1024 bytes de datos. La respuesta
se decodifica de bytes a una cadena.

*Transferencia de Cantidad (si la Identidad es Verificada):*

if "Identidad verificada" in respuesta:
    cantidad = input("Ingrese la cantidad a transferir: ")
    s.sendall(cantidad.encode('utf-8'))

Si la respuesta del servidor indica que la identidad del usuario ha sido verificada, el cliente solicita la cantidad a transferir
y la envía al servidor.

*Recepción de Respuesta Final:*

respuesta = s.recv(1024).decode('utf-8')
print(f"Respuesta del servidor: {respuesta}")

El cliente recibe la respuesta final del servidor, que puede confirmar la transacción u ofrecer información adicional.

Resumen
Este código implementa un cliente que se conecta a un servidor mediante sockets. Utiliza HMAC para asegurar la integridad de los
mensajes enviados y genera un nonce único para cada transacción, lo que ayuda a prevenir ataques de repetición. El cliente
interactúa con el usuario para registrar o iniciar sesión, y puede enviar una cantidad para transferir si la identidad del usuario
es verificada con éxito.