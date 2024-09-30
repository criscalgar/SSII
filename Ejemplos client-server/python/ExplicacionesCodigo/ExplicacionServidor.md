Este código implementa un servidor que interactúa con una base de datos MySQL para autenticar usuarios,
registrar nuevas cuentas y manejar transacciones financieras. El servidor usa verificación de integridad
mediante el uso de HMAC (Hash-based Message Authentication Code) para asegurarse de que los mensajes no
hayan sido alterados y proteger contra ataques de repetición (replay attacks). A continuación se detalla
el uso de las bibliotecas y funciones incluidas en el código.

*Importaciones y su uso*

**socket:**

Proporciona la capacidad de establecer una conexión de red entre un cliente y un servidor utilizando
sockets TCP/IP. El servidor escucha conexiones en un puerto específico y gestiona la comunicación con
los clientes a través de estos sockets.

**mysql.connector:**

Biblioteca utilizada para interactuar con una base de datos MySQL desde Python. En este código, se usa
para realizar consultas SQL, verificar la existencia de usuarios, registrar usuarios y registrar
transacciones en la base de datos.

**hmac:**

Biblioteca estándar de Python que implementa HMAC (Message Authentication Code basado en hash), un
mecanismo que asegura la integridad y autenticidad de los mensajes. Aquí se utiliza para generar un
hash criptográfico (SHA256) basado en una clave secreta compartida entre el cliente y el servidor.

**hashlib:**

Biblioteca que proporciona implementaciones de funciones hash seguras, como SHA256. Junto con hmac,
se utiliza para asegurar que los datos enviados entre el cliente y el servidor no sean modificados.

**time y os:**

Estas bibliotecas se utilizan para generar un nonce único (número usado solo una vez), que es un valor
temporalmente único que previene los replay attacks.

time obtiene la hora actual y os.getpid() proporciona el ID del proceso, combinados crean un nonce único.

*Funciones y su propósito*

**1. conectar_base_datos():**

Conecta a la base de datos MySQL usando el conector de Python. Especifica las credenciales
(user, password, etc.) y define la base de datos a la que se conectará (pai_1).

**2. verificar_usuario(nombre_usuario, db_conn):**

Consulta la base de datos para verificar si un usuario con un nombre específico ya existe. Retorna el id del
usuario si existe, o None si no lo encuentra.

**3. registrar_usuario(nombre_usuario, clave, db_conn):**

Inserta un nuevo usuario en la base de datos con el nombre de usuario y clave proporcionados. Se asegura de
que la clave esté almacenada en formato hash seguro.

**4. verificar_contraseña(nombre_usuario, clave, db_conn):**

Verifica si un usuario y su clave coinciden en la base de datos. Consulta para ver si los datos de inicio de
sesión coinciden y retorna el id del usuario si es correcto.

**5. registrar_transaccion(usuario_id, cantidad, db_conn):**

Inserta una transacción en la tabla transacciones de la base de datos, asociando un usuario (usuario_id) y una
cantidad específica.

**6. verificar_mac(mensaje, mac, nonce, nonce_list):**

Verifica la integridad del mensaje recibido comprobando si el MAC calculado (basado en la clave secreta compartida y el mensaje) coincide con el MAC enviado. Además, verifica que el nonce no se haya reutilizado para evitar ataques de repetición. Si el nonce ya ha sido procesado, se considera un ataque y el mensaje se rechaza.

**7. Manejo de la conexión de red:**

El servidor usa sockets para escuchar en HOST = "127.0.0.1" y el puerto 8080. Cada vez que un cliente se conecta, se acepta la conexión y se procesa el mensaje recibido. Los mensajes contienen una acción registrar o iniciar sesión), el nombre de usuario, la clave, un nonce y el MAC. El servidor valida el MAC para garantizar que el mensaje no fue alterado y procesa la acción según sea necesario (registrar nuevo usuario o iniciar sesión).

**8. Estructura general del ciclo del servidor:**

Una vez que un cliente se conecta, el servidor permanece en un ciclo esperando mensajes.
Los mensajes se dividen en componentes (accion, nombre_usuario, clave, nonce, mac).
El servidor verifica la integridad del mensaje con la función verificar_mac().
Dependiendo de la acción (registrar o iniciar sesión), el servidor ejecuta las funciones correspondientes y envía una respuesta al cliente. Si la autenticación es exitosa y la acción es válida, se permite que el cliente realice una transacción, que se registra en la base de datos.

*Proceso de Verificación de Integridad y Seguridad*

**MAC:**

Se usa para asegurar que los mensajes no hayan sido modificados. El servidor recibe el mensaje y el MAC. Luego recalcula el MAC usando la clave secreta y compara los resultados. Si el MAC no coincide, significa que el mensaje pudo haber sido alterado y se rechaza.

**Nonce:**

El nonce se usa para evitar ataques de repetición, donde un atacante captura un mensaje válido y lo vuelve a enviar. Al asegurar que cada mensaje tiene un nonce único (no reutilizable), el servidor puede detectar si se intenta volver a usar un mensaje anterior.

*Flujo de trabajo general:*

**Cliente envía un mensaje:**

Incluye una acción (registrar o iniciar sesión), el nombre de usuario, la clave, un nonce y un MAC que asegura la integridad del mensaje.

**Servidor recibe y valida:**

El servidor recibe el mensaje, extrae el MAC, recalcula su propio MAC usando la misma clave secreta y compara ambos. Si el MAC es válido y el nonce no ha sido usado antes, el servidor ejecuta la acción solicitada.

**Respuestas:**

Dependiendo del resultado (usuario registrado exitosamente, identidad verificada, error en el MAC), el servidor envía una respuesta al cliente.

En resumen, este código asegura la integridad y autenticidad de los mensajes entre cliente y servidor utilizando HMAC para verificar que los mensajes no han sido modificados, y utiliza nonces para protegerse de ataques de repetición.