Este código implementa un servidor que interactúa con una base de datos MySQL para autenticar usuarios,
registrar nuevas cuentas y manejar transacciones financieras. El servidor usa verificación de integridad
mediante el uso de HMAC (Hash-based Message Authentication Code) para asegurarse de que los mensajes no
hayan sido alterados y proteger contra ataques de repetición (replay attacks). A continuación se detalla
el uso de las bibliotecas y funciones incluidas en el código.

*Librerías Importadas*

**socket:** 

Esta biblioteca proporciona una interfaz para la comunicación a través de redes. Permite crear sockets que se pueden utilizar para enviar y recibir datos a través de protocolos como TCP/IP.

**mysql.connector:** 

Esta biblioteca se utiliza para interactuar con bases de datos MySQL. Permite ejecutar consultas SQL y gestionar la conexión a la base de datos.

**hmac:** 

Esta biblioteca permite crear códigos de autenticación de mensajes basados en hash (HMAC). Es útil para verificar la integridad de los mensajes, asegurando que no hayan sido alterados.

**hashlib:** 

Esta biblioteca proporciona acceso a funciones de hashing, como SHA-256, que se utilizan para generar un hash de un mensaje.

**time:** 

Se utiliza para trabajar con tiempos y fechas, en este caso, para generar un nonce único basado en el tiempo.

**os:** 

Esta biblioteca proporciona una forma de interactuar con el sistema operativo. Aquí se usa para obtener el ID del proceso, que se utiliza en la generación del nonce.

*Explicación del Código*

**Configuración y Clave Secreta**

*SECRET_KEY = b"clave_super_secreta"*

Se define una clave secreta compartida que se utiliza para la creación de HMAC. Esta clave debe mantenerse en secreto y no debe ser revelada.

**Función para Conectar a la Base de Datos**

*def conectar_base_datos():*
    *return mysql.connector.connect(*
        *host="127.0.0.1",*
        *user="root",*
        *password="root",*
        *database="pai_1",*
        *charset='utf8mb4',*
        *collation='utf8mb4_general_ci'*
    *)*

Esta función establece una conexión con la base de datos MySQL, utilizando los parámetros proporcionados (host, usuario, contraseña y nombre de la base de datos). Devuelve un objeto de conexión que se utiliza para realizar operaciones en la base de datos.

*Funciones para Manejo de Usuarios*

**Verificar si el Usuario Existe**

*def verificar_usuario(nombre_usuario, db_conn):*
    *cursor = db_conn.cursor()*
    *cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))*
    *return cursor.fetchone()*

Esta función verifica si un usuario existe en la base de datos consultando la tabla usuarios. Si el usuario existe, devuelve su ID.

**Registrar un Nuevo Usuario**

*def registrar_usuario(nombre_usuario, clave, db_conn):*
    *cursor = db_conn.cursor()*
    *cursor.execute("INSERT INTO usuarios (nombre_usuario, clave) VALUES (%s, %s)",*
                  *(nombre_usuario, clave))*
    *db_conn.commit()*
    *return cursor.lastrowid*

Esta función inserta un nuevo usuario en la base de datos. Se utilizan sentencias SQL para agregar el nombre_usuario y clave, y luego se realiza un commit para guardar los cambios.

**Verificar la Contraseña del Usuario**

*def verificar_contraseña(nombre_usuario, clave, db_conn):*
    *cursor = db_conn.cursor()*
    *cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s AND clave = %s",* 
                   *(nombre_usuario, clave))*
    *return cursor.fetchone()*

Esta función verifica si las credenciales (nombre de usuario y clave) son correctas, consultando la base de datos.

**Función para Registrar Transacciones**

*def registrar_transaccion(emisor_nombre, destinatario_nombre, cantidad, db_conn):*
    *cursor = db_conn.cursor()*
    *cursor.execute(*
        *"INSERT INTO transacciones (emisor_nombre, destinatario_nombre, cantidad) VALUES (%s, %s, %s)",* 
        *(emisor_nombre, destinatario_nombre, cantidad)*
    *)*
    *db_conn.commit()*
    *return cursor.lastrowid*

Esta función registra una transacción en la base de datos, almacenando los nombres del emisor y del destinatario, así como la cantidad transferida.

**Verificación de MAC y Nonce**

*def verificar_mac(mensaje, mac, nonce, nonce_list):*
    *mac_calculado = hmac.new(SECRET_KEY, mensaje.encode('utf-8'), hashlib.sha256).hexdigest()*
    *if mac != mac_calculado:*
        *return False*
    *if nonce in nonce_list:*
        *return False  # Replay attack detectado*
    *nonce_list.append(nonce)*
    *return True*

Esta función verifica la integridad del mensaje. Calcula un nuevo HMAC utilizando la SECRET_KEY y compara con el HMAC recibido. También comprueba si el nonce ya ha sido utilizado, para prevenir ataques de repetición.

**Configuración del Servidor**

*HOST = "127.0.0.1"*
*PORT = 8080*
*nonce_list = []  # Lista para almacenar nonces usados*

Se define la dirección y el puerto en el que el servidor escuchará las conexiones. Se inicializa una lista para rastrear los nonces utilizados.

**Iniciar el Servidor**

*with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:*
    *s.bind((HOST, PORT))*
    *s.listen()*
    *print(f"Servidor escuchando en {HOST}:{PORT}...")*

Se crea un socket TCP que se enlaza a la dirección y el puerto especificados. Luego, el servidor comienza a escuchar las conexiones entrantes.

**Ciclo Principal del Servidor**

*conn, addr = s.accept()*
*with conn:*
    *print(f"Conectado por {addr}")*

*db_conn = conectar_base_datos()*

*while True:*
    *# Recibir datos del cliente*
    *data = conn.recv(1024)*
    *if not data:*
        *break*
        
Una vez que se acepta una conexión, se establece la conexión con la base de datos. El servidor entra en un ciclo donde recibe datos del cliente. Si no se reciben datos, el bucle se rompe.

**Procesamiento de Datos Recibidos**

*datos = data.decode('utf-8').split(',')*
*if len(datos) >= 5:*
    *accion = datos[0]*
    *nombre_usuario = datos[1]*
    *clave = datos[2]*
    *nonce = datos[3]*
    *mac = datos[4]*


Los datos recibidos se decodifican y se dividen en componentes: acción (registrar o iniciar sesión), nombre de usuario, clave, nonce y MAC.

**Verificación de la Integridad del Mensaje**

*mensaje = f"{accion},{nombre_usuario},{clave},{nonce}"*
*if not verificar_mac(mensaje, mac, nonce, nonce_list):*
    *respuesta = "Error: Mensaje modificado o nonce reutilizado."*
    *conn.sendall(respuesta.encode('utf-8'))*
    *continue*

Se verifica la integridad del mensaje utilizando la función verificar_mac. Si la verificación falla, se envía un mensaje de error al cliente.

**Manejo de Acciones del Cliente**

*if accion.lower() == "registrar":*
    *if not verificar_usuario(nombre_usuario, db_conn):*
        *usuario_id = registrar_usuario(nombre_usuario, clave, db_conn)*
        *respuesta = f"Usuario '{nombre_usuario}' registrado exitosamente."*
    *else:*
        *respuesta = "El usuario ya existe."*

*elif accion.lower() == "iniciar":*
    *usuario_info = verificar_contraseña(nombre_usuario, clave, db_conn)*
    *if usuario_info:*
        *respuesta = "Identidad verificada. Por favor, indique el nombre del destinatario."*
    *else:*
        *respuesta = "Usuario o clave incorrectos."*

Dependiendo de la acción solicitada (registrar o iniciar sesión), se realiza la verificación correspondiente y se envía una respuesta adecuada al cliente.

**Verificación y Registro de Transacciones**

*if 'Identidad verificada' in respuesta:*
    *destinatario = conn.recv(1024).decode('utf-8')*
    *if not verificar_usuario(destinatario, db_conn):*
        *respuesta = "Error: El usuario destinatario no existe."*
        *conn.sendall(respuesta.encode('utf-8'))*
        *continue*
    
**Registrar la transacción**

*transaccion_id = registrar_transaccion(nombre_usuario, destinatario, cantidad, db_conn)*
*respuesta = f"Transferencia #{transaccion_id} registrada exitosamente."*
*conn.sendall(respuesta.encode('utf-8'))*

Si la identidad del usuario ha sido verificada, se procede a solicitar el nombre del destinatario. Luego, se verifica si el destinatario existe y se registra la transacción en la base de datos.

**Cierre de Conexiones**

*db_conn.close()*

Al final del bucle, se cierra la conexión con la base de datos, asegurando que todos los recursos se liberen adecuadamente.