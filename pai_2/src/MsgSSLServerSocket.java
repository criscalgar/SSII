import java.io.*;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import javax.net.ssl.*;
import org.mindrot.jbcrypt.BCrypt;
import java.sql.*;
import java.util.logging.*;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

public class MsgSSLServerSocket {
    private static final Logger logger = Logger.getLogger(MsgSSLServerSocket.class.getName());
    private static HikariDataSource dataSource;

    // Inicialización del logger y la configuración de rotación de logs
    static {
        try {
            FileHandler fh = new FileHandler("server.log", 1024 * 1024 * 5, 5, true); // 5 MB por archivo, 5 archivos rotativos
            logger.addHandler(fh);
            SimpleFormatter formatter = new SimpleFormatter();
            fh.setFormatter(formatter);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        try {
            // Configuración del pool de conexiones HikariCP
            HikariConfig config = new HikariConfig();
            config.setJdbcUrl("jdbc:mysql://127.0.0.1:3306/pai_2");
            config.setUsername("root");
            config.setPassword("root");
            config.setMaximumPoolSize(300); // Se permite hasta 300 conexiones simultáneas
            dataSource = new HikariDataSource(config);

            String keyStorePath = "certs/serverkeystore.jks";
            String keyStorePassword = "serverpassword";

            // Cargar el keystore del servidor
            KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
            try (FileInputStream keyStoreStream = new FileInputStream(keyStorePath)) {
                keyStore.load(keyStoreStream, keyStorePassword.toCharArray());
            }

            // Configurar el contexto SSL
            SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            keyManagerFactory.init(keyStore, keyStorePassword.toCharArray());
            sslContext.init(keyManagerFactory.getKeyManagers(), null, null);

            // Crear un socket SSL en el servidor
            SSLServerSocketFactory factory = sslContext.getServerSocketFactory();
            SSLServerSocket serverSocket = (SSLServerSocket) factory.createServerSocket(3343);

            // Configurar Cipher Suites para TLSv1.3
            serverSocket.setEnabledCipherSuites(new String[]{
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256"
            });

            logger.info("Servidor SSL escuchando en el puerto 3343...");

            // Registrar usuarios iniciales
            registerInitialUsers();

            // Esperar a que los clientes se conecten
            while (true) {
                SSLSocket clientSocket = (SSLSocket) serverSocket.accept();
                new Thread(() -> handleClient(clientSocket)).start();
            }

        } catch (IOException | GeneralSecurityException e) {
            logger.log(Level.SEVERE, "Error en el servidor", e);
        }
    }

    // Manejar la conexión del cliente
    private static void handleClient(SSLSocket clientSocket) {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
             PrintWriter output = new PrintWriter(new OutputStreamWriter(clientSocket.getOutputStream()), true)) {

            boolean authenticated = false;

            // Proceso de autenticación
            while (!authenticated) {
                String line;
                if ((line = input.readLine()) != null) {
                    String[] parts = line.split(":");

                    // Autenticación del cliente
                    if (parts.length == 3 && "CREDENTIALS".equals(parts[0])) {
                        String username = parts[1].trim().toLowerCase();
                        String password = parts[2];

                        // Verificar si las credenciales son correctas
                        if (authenticate(username, password)) {
                            authenticated = true;
                            output.println("Autenticación exitosa.");
                        } else {
                            output.println("Autenticación fallida.");
                        }
                    }
                }
            }

            // Verificación del usuario destino y manejo de mensajes
            String line;
            while ((line = input.readLine()) != null) {
                String[] parts = line.split(":");

                // Verificación del usuario destino
                if (parts.length == 2 && "VERIFY_USER".equals(parts[0])) {
                    String destinationUser = parts[1].trim().toLowerCase();
                    if (userExists(destinationUser)) {
                        output.println("Usuario existe");
                    } else {
                        output.println("Usuario no existe");
                    }
                }
                // Recepción y almacenamiento de mensajes
                else if (parts.length == 4 && "MENSAJE".equals(parts[0])) {
                    String sourceUser = parts[1];
                    String destinationUser = parts[2];
                    String msgContent = parts[3];

                    // Guardar el mensaje en la base de datos
                    storeMessage(sourceUser, destinationUser, msgContent);
                    output.println("Mensaje recibido: " + msgContent);
                } else {
                    output.println("Formato de mensaje incorrecto.");
                }
            }

        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error al manejar el cliente", e);
        } finally {
            try {
                clientSocket.close();
            } catch (IOException e) {
                logger.log(Level.SEVERE, "Error al cerrar el socket del cliente", e);
            }
        }
    }

    // Método para autenticar al usuario
    private static boolean authenticate(String username, String password) {
        try (Connection connection = dataSource.getConnection()) {
            String query = "SELECT password FROM usuarios WHERE LOWER(username) = ?";
            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, username);
                ResultSet resultSet = statement.executeQuery();
                if (resultSet.next()) {
                    String hashedPassword = resultSet.getString("password");
                    return BCrypt.checkpw(password, hashedPassword);
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error en la autenticación", e);
        }
        return false;
    }

    // Método para verificar si el usuario destino existe
    private static boolean userExists(String username) {
        try (Connection connection = dataSource.getConnection()) {
            String query = "SELECT COUNT(*) FROM usuarios WHERE LOWER(username) = ?";
            try (PreparedStatement statement = connection.prepareStatement(query)) {
                statement.setString(1, username);
                ResultSet resultSet = statement.executeQuery();
                if (resultSet.next()) {
                    return resultSet.getInt(1) > 0;
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error al verificar existencia de usuario", e);
        }
        return false;
    }

    // Método para almacenar el mensaje en la base de datos
    private static void storeMessage(String sourceUser, String destinationUser, String message) {
        String query = "INSERT INTO mensajes(user_source, user_destination, message) VALUES (?, ?, ?)";

        try (Connection connection = dataSource.getConnection();
             PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, sourceUser);
            statement.setString(2, destinationUser);
            statement.setString(3, message);
            statement.executeUpdate();
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error al almacenar el mensaje", e);
        }
    }

    // Método para registrar usuarios iniciales
    private static void registerInitialUsers() {
        String[][] initialUsers = {
            {"cristina calderon garcia", "123456"},
            {"blanca garcia alonso", "123456"},
            {"yassine nacif berrada", "123456"},
            {"testuser", "testpassword"}
        };

        try (Connection connection = dataSource.getConnection()) {
            for (String[] user : initialUsers) {
                String username = user[0].toLowerCase();
                String plainPassword = user[1];
                String hashedPassword = BCrypt.hashpw(plainPassword, BCrypt.gensalt());

                if (!userExists(username)) {
                    String query = "INSERT INTO usuarios(username, password) VALUES (?, ?)";
                    try (PreparedStatement statement = connection.prepareStatement(query)) {
                        statement.setString(1, username);
                        statement.setString(2, hashedPassword);
                        statement.executeUpdate();
                        logger.info("Usuario registrado: " + username);
                    }
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error al registrar usuarios iniciales", e);
        }
    }
}