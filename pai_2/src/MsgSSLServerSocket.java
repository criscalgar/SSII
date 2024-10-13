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
    private static final String DB_URL = "jdbc:mysql://localhost:3306/pai_2"; // Cambia por tu URL
    private static final String DB_USER = "root"; // Cambia por tu usuario
    private static final String DB_PASSWORD = "root"; // Cambia por tu contraseña
    private static final Logger logger = Logger.getLogger(MsgSSLServerSocket.class.getName());

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
            String keyStorePath = "serverkeystore.jks"; 
            String keyStorePassword = "serverpassword"; 

            KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
            try (FileInputStream keyStoreStream = new FileInputStream(keyStorePath)) {
                keyStore.load(keyStoreStream, keyStorePassword.toCharArray());
            }

            SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            keyManagerFactory.init(keyStore, keyStorePassword.toCharArray());
            sslContext.init(keyManagerFactory.getKeyManagers(), null, null);

            SSLServerSocketFactory factory = sslContext.getServerSocketFactory();
            SSLServerSocket serverSocket = (SSLServerSocket) factory.createServerSocket(3343);
            
            logger.info("Servidor SSL escuchando en el puerto 3343...");

            registerInitialUsers();

            while (true) {
                SSLSocket clientSocket = (SSLSocket) serverSocket.accept();
                new Thread(() -> handleClient(clientSocket)).start();
            }

        } catch (IOException | GeneralSecurityException e) {
            logger.log(Level.SEVERE, "Error en el servidor", e);
        }
    }

    private static void handleClient(SSLSocket clientSocket) {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
             PrintWriter output = new PrintWriter(new OutputStreamWriter(clientSocket.getOutputStream()), true)) {

            boolean authenticated = false;

            while (!authenticated) {
                // Leer las credenciales enviadas por el cliente
                String line;
                if ((line = input.readLine()) != null) {
                    String[] parts = line.split(":");
                    if (parts.length == 3 && "CREDENTIALS".equals(parts[0])) {
                        String username = parts[1].trim().toLowerCase().replaceAll("\\s+", ""); 
                        String password = parts[2];

                        // Verificar si el usuario y la contraseña son correctos
                        if (authenticate(username, password)) {
                            authenticated = true;
                            output.println("Autenticación exitosa.");

                            String message = "";
                            while (message == null || message.trim().isEmpty()) {
                                // Leer el mensaje del cliente
                                message = input.readLine();
                                if (message == null || message.trim().isEmpty()) {
                                    output.println("El mensaje está vacío. Por favor, repita su mensaje."); 
                                }
                            }

                            String[] messageParts = message.split(":");
                            if (messageParts.length == 4 && "MENSAJE".equals(messageParts[0])) {
                                String sourceUser = messageParts[1]; // usuario fuente
                                String destinationUser = messageParts[2]; // usuario destino
                                String msgContent = messageParts[3]; // contenido del mensaje

                                storeMessage(sourceUser, destinationUser, msgContent); // Almacenar el mensaje en la base de datos
                                output.println("Mensaje recibido: " + msgContent);
                            } else {
                                output.println("Formato de mensaje incorrecto.");
                            }
                        } else {
                            output.println("Autenticación fallida. Por favor, vuelva a ingresar sus credenciales."); // Mensaje de error
                        }
                    } else {
                        output.println("Formato de credenciales incorrecto. Por favor, envíe de nuevo.");
                    }
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

    private static void registerInitialUsers() {
        String[][] initialUsers = {
            {"cristina calderon garcia", "123456"}, 
            {"blanca garcia alonso", "123456"} 
        };

        try (Connection connection = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            for (String[] user : initialUsers) {
                String username = user[0].trim().toLowerCase().replaceAll("\\s+", ""); 
                String plainPassword = user[1];
                String hashedPassword = BCrypt.hashpw(plainPassword, BCrypt.gensalt());

                if (!userExists(username)) {
                    String query = "INSERT INTO usuarios (username, password) VALUES (?, ?)";
                    try (PreparedStatement statement = connection.prepareStatement(query)) {
                        statement.setString(1, username);
                        statement.setString(2, hashedPassword);
                        statement.executeUpdate();
                    }
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error al registrar usuarios iniciales", e);
        }
    }

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

    private static void storeMessage(String sourceUser, String destinationUser, String message) {
        String query = "INSERT INTO mensajes (source_user, destination_user, message) VALUES (?, ?, ?)"; // Cambia la tabla y columnas según tu esquema

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