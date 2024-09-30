Este código implementa la funcionalidad básica de un cliente para un sistema de autenticación y
transacciones usando comunicación por sockets. Utiliza la librería socket para la comunicación
en red y la librería hmac para asegurar la integridad y autenticidad de los mensajes enviados 
entre el cliente y el servidor. 

*Librerías implementadas:*

**socket:**

 Proporciona la interfaz para comunicación entre redes. Aquí se utiliza para crear una conexión TCP entre el cliente y el servidor.

**hmac:**

 Permite crear un código de autenticación de mensaje (MAC) utilizando una clave secreta y un algoritmo hash. Se usa para asegurar la integridad y autenticidad de los mensajes intercambiados.

**hashlib:**

 Proporciona acceso a varias funciones hash seguras, como sha256, la cual se usa en combinación con HMAC para generar el MAC.

**time:**

 Se utiliza para obtener la marca de tiempo actual (timestamp) y generar un número único para cada transacción (nonce).

**os:**

 Se usa para obtener el ID de proceso del cliente (os.getpid()), lo que ayuda a generar el nonce.

*Explicación de las funciones:*

*SECRET_KEY:*

 Es una clave secreta compartida entre el cliente y el servidor para la creación del HMAC. Esta clave es utilizada para garantizar que el mensaje no sea manipulado durante el envío.

**generar_nonce():**

 Esta función genera un valor único (nonce) para cada transacción combinando el timestamp actual y el ID del proceso del cliente. Esto asegura que cada mensaje sea único y evite ataques de repetición (replay attacks).

**generar_mac(mensaje):**

 Esta función genera un código de autenticación de mensaje (MAC) usando HMAC con la clave secreta SECRET_KEY y el algoritmo SHA-256. El MAC asegura que el mensaje no ha sido alterado durante la transmisión.

*Flujo del programa:*

**Conexión con el servidor:**

Se crea un socket usando la familia de direcciones AF_INET (IPv4) y el protocolo de transporte SOCK_STREAM (TCP). El cliente se conecta al servidor en la dirección 127.0.0.1 (localhost) y el puerto 8080.

**Selección de acción:**

El usuario puede seleccionar entre "Registrar" (para crear un nuevo usuario) o "Iniciar" (para iniciar sesión con un usuario existente).
Si la acción es inválida, el cliente se desconecta.

**Ingreso de datos:**

El usuario ingresa su nombre de usuario (que se convierte en minúsculas para normalizar la entrada) y su contraseña.
Generación de un nonce:

Se crea un valor único utilizando generar_nonce(), el cual se usará para prevenir ataques de repetición.
Generación de MAC:

El mensaje compuesto por la acción, nombre de usuario, clave y nonce es protegido mediante HMAC usando la clave secreta.

**Envío de datos:**

Se envían al servidor los datos del mensaje junto con el MAC generado, todo en un solo paquete.

**Respuesta del servidor:**

El cliente recibe la respuesta del servidor, que puede indicar si la identidad del usuario ha sido verificada o no.

**Interacción adicional (transacción):**

Si la identidad ha sido verificada, el cliente puede ingresar el nombre del destinatario (también normalizado a minúsculas). Tras la verificación del destinatario, se solicita al usuario la cantidad a transferir, la cual también es enviada al servidor.

*Funcionalidad clave:*

**Este cliente permite:**

Autenticar usuarios y verificar su identidad usando HMAC y un nonce único para proteger los mensajes.
Realizar transacciones tras la verificación exitosa de la identidad del usuario y del destinatario.
Evitar ataques de repetición mediante el uso de un nonce.
Asegurar que los mensajes no sean modificados durante la transmisión, ya que el servidor puede validar el HMAC generado.
Este sistema básico asegura integridad y autenticidad en la comunicación, aunque no implementa otros aspectos de seguridad como el cifrado de los mensajes en tránsito, lo cual sería recomendable en un entorno real.