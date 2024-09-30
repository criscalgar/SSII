Este código implementa un servidor que maneja la autenticación de usuarios y transacciones entre ellos mediante comunicación con un cliente a través de sockets. Además, integra una base de datos MySQL/MariaDB para almacenar usuarios y transacciones, usando bcrypt para asegurar las contraseñas, y HMAC para proteger la integridad de los mensajes.

*Librerías implementadas:*

**socket:**

Se utiliza para la comunicación entre el servidor y el cliente a través de sockets TCP.

**mysql.connector:**

Permite conectarse a una base de datos MySQL o MariaDB para realizar operaciones como consultas y modificaciones.

**hmac:**

Genera códigos de autenticación de mensaje (MAC) utilizando una clave secreta para asegurar la integridad y autenticidad del mensaje.

**hashlib:**

Proporciona funciones de hashing, en este caso, sha256 es utilizado junto con hmac.

**bcrypt:** 

Utilizado para hashear las contraseñas de los usuarios, permitiendo una manera segura de almacenarlas y verificarlas.

**time y os:**

Utilizadas para generar nonces únicos que evitan ataques de repetición.

*Explicación de la funcionalidad:*

**SECRET_KEY:**

Es una clave secreta compartida entre el cliente y el servidor, utilizada para generar el MAC que protege los mensajes.

*Conexión a la base de datos (conectar_base_datos):*

Esta función establece una conexión con la base de datos MySQL/MariaDB. Usa los parámetros de conexión como host, user, password, database, charset, y collation.

*Verificación y manejo de usuarios:*

**verificar_usuario(nombre_usuario, db_conn):**

Verifica si un usuario ya existe en la base de datos. Convierte el nombre de usuario a minúsculas para evitar problemas de sensibilidad de mayúsculas/minúsculas.

**registrar_usuario(nombre_usuario, clave, db_conn):**

Registra un nuevo usuario en la base de datos. La contraseña es hasheada con bcrypt antes de ser almacenada. Esto asegura que incluso si la base de datos es comprometida, las contraseñas no se verán comprometidas directamente.

**verificar_contraseña(nombre_usuario, clave, db_conn):**

Verifica si la contraseña proporcionada por el usuario coincide con la clave hasheada almacenada en la base de datos. Utiliza bcrypt.checkpw para comparar la clave proporcionada con la clave hasheada.

**Registro de transacciones (registrar_transaccion):**

Esta función inserta un registro de transacción en la base de datos, con el nombre del emisor, destinatario y la cantidad transferida.

*Verificación de integridad del mensaje:*

**verificar_mac(mensaje, mac, nonce, nonce_list):**

Esta función asegura la integridad del mensaje recibido por el servidor. Verifica el MAC del mensaje y se asegura de que el nonce no haya sido utilizado previamente, previniendo ataques de repetición.

**Configuración y funcionamiento del servidor:**

Se utiliza socket para crear un servidor TCP que escuche en la dirección 127.0.0.1 y el puerto 8080. El servidor espera conexiones de los clientes.

Al aceptar una conexión, se maneja la autenticación de usuarios. El cliente envía su acción (registrar o iniciar sesión), nombre de usuario, clave, nonce, y MAC. El servidor verifica la integridad del mensaje utilizando verificar_mac.

**Registro de usuarios o inicio de sesión:**

Si el cliente selecciona la acción "registrar", el servidor verifica si el usuario ya existe. Si no existe, lo registra con la contraseña hasheada.

Si el cliente selecciona la acción "iniciar", el servidor verifica si la contraseña proporcionada es correcta comparándola con el hash almacenado.

**Realización de transacciones:**

Una vez autenticado el usuario, puede realizar una transferencia ingresando el nombre del destinatario y la cantidad a transferir. El servidor verifica que el destinatario exista y, si es válido, registra la transacción en la base de datos.

*Seguridad implementada:*

Uso de bcrypt para hashear contraseñas: bcrypt es una herramienta estándar en seguridad que proporciona hashing seguro de contraseñas, haciendo más difícil que los atacantes puedan obtener las contraseñas originales en caso de un compromiso de la base de datos.

**Verificación de MAC (Message Authentication Code):**

Garantiza la integridad y autenticidad de los mensajes intercambiados. Si el MAC no coincide, el servidor sabe que el mensaje fue alterado.

**Uso de nonces:**

Cada transacción tiene un nonce único, lo que impide que un atacante capture y vuelva a enviar mensajes anteriores (ataque de repetición).

**Flujo del programa:**

El servidor se inicia y escucha en la dirección 127.0.0.1:8080.
Cuando un cliente se conecta, el servidor recibe los datos que incluyen la acción, el nombre de usuario, la clave, el nonce y el MAC.
El servidor verifica que el MAC y el nonce sean válidos.

*Dependiendo de la acción, el servidor:*

Registra un nuevo usuario o inicia sesión verificando la contraseña hasheada.
Si la autenticación es exitosa, el usuario puede realizar una transacción indicando el destinatario y la cantidad.
El servidor verifica que el destinatario exista y luego registra la transacción en la base de datos.
Este código tiene una buena estructura básica para asegurar las contraseñas de los usuarios y proteger la integridad de los mensajes, aunque sería recomendable implementar cifrado en las comunicaciones para una mayor seguridad en un entorno real.


*POR QUÉ USAR BCRYPT*

Usar bcrypt para hashear contraseñas tiene varias ventajas importantes. 

**1. Seguridad Robusta**
*->* Hasheo unidireccional: bcrypt convierte la contraseña en un hash que no puede ser revertido. Esto
     significa que incluso si alguien obtiene acceso a la base de datos, no podrá recuperar las contraseñas originales.
     Dificultad de Ataques de Fuerza Bruta: bcrypt permite ajustar la complejidad del hash a través de un
     factor de costo. Esto hace que el proceso de hash sea más lento y, por lo tanto, más difícil para los atacantes que intentan adivinar contraseñas a través de ataques de fuerza bruta.

**2. Salting Automático**
*->* bcrypt genera automáticamente un salt único para cada contraseña. Esto significa que incluso si dos
     usuarios tienen la misma contraseña, los hashes serán diferentes, lo que previene ataques de tablas arcoíris.

**3. Resistencia a la Computación Moderna**
*->* bcrypt está diseñado para ser resistente frente a ataques que utilizan hardware moderno, como GPUs. 
     A medida que la tecnología avanza, se pueden hacer más rápidas las operaciones de hash; sin embargo, bcrypt puede ajustarse a los avances en el hardware, aumentando el tiempo de hash según sea necesario.

**4. Estándar de la Industria**
*->* bcrypt se ha convertido en un estándar de facto para el almacenamiento seguro de contraseñas. Es   
     ampliamente utilizado y ha sido revisado por expertos en seguridad, lo que le da un alto nivel de confianza.

**5. Facilidad de Implementación**
*->* La mayoría de los lenguajes de programación y marcos tienen bibliotecas bien soportadas para 
     bcrypt, lo que facilita su integración en aplicaciones existentes.

**6. Interoperabilidad**
*->* Aunque estés utilizando HeidiSQL para gestionar tu base de datos, puedes utilizar bcrypt en tu 
     aplicación (en el servidor) para manejar el hashing de contraseñas. Esto permite mantener las contraseñas seguras incluso si la base de datos es vulnerable.

**Conclusión**
Usar bcrypt para hashear contraseñas es una práctica de seguridad recomendada que ayuda a proteger las contraseñas de los usuarios en tu aplicación. Al hacerlo, puedes reducir significativamente el riesgo de comprometer las credenciales de los usuarios y mejorar la seguridad general de tu sistema. Si tienes más preguntas o necesitas más información sobre su implementación.