import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import javax.net.ssl.*;
import javax.swing.JOptionPane;
import javax.swing.JPasswordField;
import java.util.logging.*;

public class MsgSSLClientSocket {
    private static final Logger logger = Logger.getLogger(MsgSSLClientSocket.class.getName());

    // Inicialización del logger
    static {
        try {
            FileHandler fh = new FileHandler("client.log", true);
            logger.addHandler(fh);
            SimpleFormatter formatter = new SimpleFormatter();
            fh.setFormatter(formatter);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        try {
            // Cargar el keystore del cliente
            String keyStorePath = "certs/clientkeystore.jks"; // Ruta al client keystore
            String keyStorePassword = "clientpassword"; // Cambia por tu contraseña

            KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
            try (FileInputStream keyStoreStream = new FileInputStream(keyStorePath)) {
                keyStore.load(keyStoreStream, keyStorePassword.toCharArray());
            }

            // Cargar el truststore del cliente
            String trustStorePath = "certs/truststore.jks"; // Ruta al truststore
            String trustStorePassword = "trustpassword"; // Cambia por tu contraseña

            KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
            try (FileInputStream trustStoreStream = new FileInputStream(trustStorePath)) {
                trustStore.load(trustStoreStream, trustStorePassword.toCharArray());
            }

            // Configurar SSL
            SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
            TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStore);

            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            keyManagerFactory.init(keyStore, keyStorePassword.toCharArray());

            sslContext.init(keyManagerFactory.getKeyManagers(), trustManagerFactory.getTrustManagers(), null);

            SSLSocketFactory factory = sslContext.getSocketFactory();
            try (SSLSocket socket = (SSLSocket) factory.createSocket("localhost", 3343);
                 PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()), true);
                 BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {

                // Validación de nombre de usuario
                String username = null;
                while (username == null || username.trim().isEmpty()) {
                    username = JOptionPane.showInputDialog("Ingrese su nombre de usuario:");
                    if (username == null || username.trim().isEmpty()) {
                        JOptionPane.showMessageDialog(null, "El nombre de usuario no puede estar vacío.");
                    }
                }

                // Usamos JPasswordField para ocultar la entrada de la contraseña, dentro de un JOptionPane
                JPasswordField passwordField = new JPasswordField();
                Object[] message = {"Ingrese su contraseña:", passwordField};
                int option = JOptionPane.showConfirmDialog(null, message, "Contraseña", JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE);
                String password = null;

                if (option == JOptionPane.OK_OPTION) {
                    password = new String(passwordField.getPassword());
                }

                if (password == null || password.trim().isEmpty()) {
                    JOptionPane.showMessageDialog(null, "La contraseña no puede estar vacía.");
                    return; // Cancelar la ejecución si no se ingresa una contraseña
                }

                // Enviar credenciales al servidor
                output.println("CREDENTIALS:" + username + ":" + password);

                String response = input.readLine();
                System.out.println("Respuesta del servidor: " + response);

                if ("Autenticación exitosa.".equals(response)) {
                    // Bucle para validar el usuario destino
                    boolean validUser = false;
                    String destinationUser = null;

                    while (!validUser) {
                        // Validación de usuario destino
                        while (destinationUser == null || destinationUser.trim().isEmpty()) {
                            destinationUser = JOptionPane.showInputDialog("Ingrese el usuario destino:");
                            if (destinationUser == null || destinationUser.trim().isEmpty()) {
                                JOptionPane.showMessageDialog(null, "El usuario destino no puede estar vacío.");
                            }
                        }

                        // Enviar solicitud de verificación de usuario destino
                        output.println("VERIFY_USER:" + destinationUser);
                        response = input.readLine();

                        if ("Usuario existe".equals(response)) {
                            JOptionPane.showMessageDialog(null, "El usuario destino es válido.");
                            validUser = true;
                        } else if ("Usuario no existe".equals(response)) {
                            JOptionPane.showMessageDialog(null, "El usuario destino no existe. Por favor, inténtelo de nuevo.");
                            destinationUser = null; // Reiniciar el valor del usuario destino
                        } else {
                            JOptionPane.showMessageDialog(null, "Error en la verificación. Cerrando cliente.");
                            break;
                        }
                    }

                    // Validación del mensaje
                    String messageContent = null;
                    while (messageContent == null || messageContent.trim().isEmpty()) {
                        messageContent = JOptionPane.showInputDialog("Ingrese su mensaje:");
                        if (messageContent == null || messageContent.trim().isEmpty()) {
                            JOptionPane.showMessageDialog(null, "El mensaje no puede estar vacío.");
                        }
                    }

                    // Enviar mensaje al servidor
                    output.println("MENSAJE:" + username + ":" + destinationUser + ":" + messageContent);
                    response = input.readLine();
                    System.out.println("Respuesta del servidor: " + response);
                    JOptionPane.showMessageDialog(null, response); // Mostrar la respuesta en un cuadro de diálogo

                } else {
                    JOptionPane.showMessageDialog(null, "Autenticación fallida. Cerrando cliente.");
                }

            } catch (IOException e) {
                logger.log(Level.SEVERE, "Error en la conexión del cliente", e);
            }
        } catch (IOException | GeneralSecurityException e) {
            logger.log(Level.SEVERE, "Error al iniciar el cliente", e);
        }
    }
}