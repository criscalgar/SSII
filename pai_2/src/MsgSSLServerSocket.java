import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import javax.net.ssl.*;
import org.mindrot.jbcrypt.BCrypt;
import java.sql.*;
import java.util.logging.*;

public class MsgSSLServerSocket {
    private static final String DB_URL = "jdbc:mysql://192.168.0.92:3306/pai_2"; // Cambia por tu URL de la base de datos
    private static final String DB_USER = "ssii"; // Cambia por tu usuario
    private static final String DB_PASSWORD = "ssii"; // Cambia por tu contraseña
    private static final Logger logger = Logger.getLogger(MsgSSLServerSocket.class.getName());

    // Inicialización del logger
    static {
        try {
            FileHandler fh = new FileHandler("server.log", true);
            logger.addHandler(fh);
            SimpleFormatter formatter = new SimpleFormatter();
            fh.setFormatter(formatter);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        try {
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
                        String username = parts[1].trim().toLowerCase(); // Convertir a minúsculas
                        String password = parts[2];

                        // Verificar si las credenciales son correctas
                        if (authenticate(username, password)) {
                            authenticated = true;
                            output.println("Autenticación exitosa.");
                        } else {
                            output.println("Autenticación fallida. Por favor, vuelva a ingresar sus credenciales.");
                        }
                    }
                }
            }

            // Verificar el usuario destino y manejar el envío de mensajes
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
                    String sourceUser = parts[1]; // Usuario que envía
                    String destinationUser = parts[2]; // Usuario destino
                    String msgContent = parts[3]; // Contenido del mensaje

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
        try (Connection connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
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
        try (Connection connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
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

    // Método para registrar los usuarios iniciales
    private static void registerInitialUsers() {
        String[][] initialUsers = {
            {"cristina calderon garcia", "123456"}, 
            {"blanca garcia alonso", "123456"},
            {"yassine nacif berrada", "123456"} 
        };

        try (Connection connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            for (String[] user : initialUsers) {
                String username = user[0]; // Mantener los espacios en blanco
                String plainPassword = user[1];
                String hashedPassword = BCrypt.hashpw(plainPassword, BCrypt.gensalt());

                if (!userExists(username)) {
                    String query = "INSERT INTO usuarios(username, password) VALUES (?, ?)";
                    try (PreparedStatement statement = connection.prepareStatement(query)) {
                        statement.setString(1, username.toLowerCase()); // Almacenar en minúsculas
                        statement.setString(2, hashedPassword);
                        statement.executeUpdate();
                        logger.info("Usuario registrado: " + username);
                    }
                } else {
                    logger.warning("El usuario ya existe: " + username);
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error al registrar usuarios iniciales", e);
        }
    }

    // Método para almacenar el mensaje en la base de datos
    private static void storeMessage(String sourceUser, String destinationUser, String message) {
        String query = "INSERT INTO mensajes(user_source, user_destination, message) VALUES (?, ?, ?)"; // Cambia la tabla y columnas según tu esquema

        try (Connection connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
             PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, sourceUser);
            statement.setString(2, destinationUser);
            statement.setString(3, message);
            statement.executeUpdate();
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error al almacenar el mensaje", e);
        }
    }
}
