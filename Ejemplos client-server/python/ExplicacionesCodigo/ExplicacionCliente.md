*Librerías Importadas*

**socket:**

Esta biblioteca es parte de la biblioteca estándar de Python y se utiliza para crear
conexiones de red. Permite que los programas se comuniquen a través de la red utilizando 
sockets, que son puntos finales para el envío y recepción de datos.

**hmac:**

Esta biblioteca se utiliza para implementar HMAC (Hash-based Message Authentication Code),
un mecanismo que combina una función hash con una clave secreta para proporcionar
autenticación y asegurar la integridad de los datos.

**hashlib:** 

Esta biblioteca proporciona funciones para calcular hashes usando varios algoritmos, como
SHA-256. Se utiliza aquí para generar el hash necesario para el MAC.

**time:** 

Proporciona funciones relacionadas con el tiempo, como obtener el tiempo actual. Se utiliza
en este código para generar un nonce único.

**os:**

Permite interactuar con el sistema operativo. En este caso, se utiliza para obtener el ID del
proceso actual (os.getpid()), que se combina con el tiempo para generar un nonce único.

*Descripción del Código*

**Clave Secreta:**

*SECRET_KEY = b"clave_super_secreta"*

Se define una clave secreta compartida entre el cliente y el servidor. Esta clave es fundamental
para la generación del código de autenticación del mensaje (MAC), asegurando que solo las partes
que conocen esta clave puedan verificar la integridad de los datos.

**Generación de Nonce:**

*def generar_nonce():*
    *return str(int(time.time())) + str(os.getpid())*

La función generar_nonce crea un nonce único combinando el tiempo actual (en segundos desde la época)
con el ID del proceso. Esto garantiza que cada nonce sea diferente, lo que es crucial para prevenir
ataques de repetición. Un nonce es un número que se utiliza una vez para asegurar que cada solicitud
es única.

**Generación de MAC:**

*def generar_mac(mensaje):*
    *return hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()*

Esta función genera un MAC utilizando HMAC con el algoritmo SHA-256. Recibe un mensaje (en forma de cadena), lo codifica en bytes y utiliza la SECRET_KEY para generar un hash que actúa como código de autenticación. El resultado se devuelve en forma de cadena hexadecimal.

**Configuración del Cliente:**

*HOST = "127.0.0.1"*
*PORT = 8080*

Se especifican la dirección IP y el puerto del servidor al que se conectará el cliente. Aquí, 127.0.0.1 se refiere a localhost, lo que significa que el cliente se está conectando a un servidor que se ejecuta en la misma máquina.

**Conexión al Servidor:**

*with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:*
    *s.connect((HOST, PORT))*

Se crea un socket TCP y se conecta al servidor especificado en HOST y PORT. La instrucción with asegura que el socket se cierre adecuadamente al final del bloque, liberando los recursos del sistema.

**Interacción con el Usuario:**

*accion = input("Ingrese:\n\n-'Registrar' para crear un nuevo usuario\n-'Iniciar' para iniciar sesión\n\nAccion a realizar: ")*
*nombre_usuario = input("\nIngrese el nombre de usuario: ")*
*clave = input("\nIngrese la clave: ")*

Se le pide al usuario que elija una acción, ya sea registrarse o iniciar sesión, y que proporcione su nombre de usuario y contraseña.

**Generación del Nonce y Formateo del Mensaje:**

*nonce = generar_nonce()*
*mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"*

Se genera un nonce único y se crea un mensaje que contiene la acción elegida, el nombre de usuario, la clave y el nonce. Este mensaje se utilizará para la autenticación y para la comunicación con el servidor.

**Generación del MAC:**

*mac = generar_mac(mensaje)*

Se genera el MAC para el mensaje utilizando la función generar_mac. Esto asegura que el mensaje no haya sido modificado durante la transmisión.

**Envío de Datos al Servidor:**

*datos = f"{mensaje},{mac}"*
*s.sendall(datos.encode('utf-8'))*

Se combinan el mensaje y el MAC en una sola cadena, que se codifica en bytes y se envía al servidor usando sendall. Esta función asegura que todos los datos sean enviados correctamente.

**Recepción de la Respuesta del Servidor:**

*respuesta = s.recv(1024).decode('utf-8')*
*print(f"\n{respuesta}")*

El cliente espera y recibe una respuesta del servidor. recv(1024) indica que se recibirán hasta 1024 bytes de datos. La respuesta se decodifica de bytes a una cadena y se imprime.

**Transferencia de Cantidad (si la Identidad es Verificada):**

*if "Identidad verificada" in respuesta:*
    *destinatario = input("\nIngrese el nombre del destinatario: ")*
    *s.sendall(destinatario.encode('utf-8'))*

Si la respuesta del servidor indica que la identidad del usuario ha sido verificada, el cliente solicita el nombre del destinatario y lo envía al servidor.

**Recepción de Respuesta sobre el Destinatario:**

*respuesta = s.recv(1024).decode('utf-8')*
*print(f"\n{respuesta}")*

El cliente recibe una respuesta sobre la verificación del destinatario y la imprime. Esto puede confirmar si el destinatario existe o está habilitado para recibir transferencias.

**Ingreso y Envío de la Cantidad a Transferir:**

*if "verificado" in respuesta:*
    *cantidad = input("\nIngrese la cantidad a transferir: ")*
    *s.sendall(cantidad.encode('utf-8'))*

Si el destinatario es verificado, se solicita al usuario que ingrese la cantidad que desea transferir y se envía esta cantidad al servidor.

**Recepción de Respuesta Final:**

*respuesta = s.recv(1024).decode('utf-8')*
*print(f"\n{respuesta}")*

Finalmente, el cliente espera y recibe la respuesta final del servidor, que puede confirmar que la transferencia se ha realizado con éxito o proporcionar información adicional.

**Resumen**
Este código implementa un cliente que se conecta a un servidor utilizando sockets. Utiliza HMAC para asegurar la integridad de los mensajes y genera un nonce único para cada transacción, ayudando a prevenir ataques de repetición. El cliente interactúa con el usuario para registrar o iniciar sesión y permite transferencias de dinero a otros usuarios, verificando tanto la identidad del usuario como la del destinatario antes de procesar la transacción.