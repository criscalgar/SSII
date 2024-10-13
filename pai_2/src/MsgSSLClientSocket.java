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
import java.util.logging.*;

public class MsgSSLClientSocket {
    private static final Logger logger = Logger.getLogger(MsgSSLClientSocket.class.getName());

    // Inicializa el logger
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
            String keyStorePath = "clientkeystore.jks"; // Ruta al client keystore
            String keyStorePassword = "clientpassword"; // Cambia por tu contraseña

            KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
            try (FileInputStream keyStoreStream = new FileInputStream(keyStorePath)) {
                keyStore.load(keyStoreStream, keyStorePassword.toCharArray());
            }

            // Cargar el truststore del cliente
            String trustStorePath = "truststore.jks"; // Ruta al truststore
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

                // Autenticación
                String username = JOptionPane.showInputDialog("Ingrese su nombre de usuario:");
                String password = JOptionPane.showInputDialog("Ingrese su contraseña:");

                output.println("CREDENTIALS:" + username + ":" + password);

                String response = input.readLine();
                System.out.println("Respuesta del servidor: " + response);

                if ("Autenticación exitosa.".equals(response)) {
                    // Enviar mensaje
                    String destinationUser = JOptionPane.showInputDialog("Ingrese el usuario destino:");
                    String message = "";
                    
                    while (message == null || message.trim().isEmpty()) {
                        message = JOptionPane.showInputDialog("Ingrese su mensaje:");
                        if (message == null || message.trim().isEmpty()) {
                            JOptionPane.showMessageDialog(null, "El mensaje está vacío. Por favor, ingréselo de nuevo."); 
                        }
                    }

                    output.println("MENSAJE:" + username + ":" + destinationUser + ":" + message);
                    response = input.readLine();
                    System.out.println("Respuesta del servidor: " + response);
                    JOptionPane.showMessageDialog(null, response); // Mensaje recibido en una ventana de diálogo
                } else {
                    JOptionPane.showMessageDialog(null, "Autenticación fallida. Cerrando cliente."); // Mensaje de error
                }

            } catch (IOException e) {
                logger.log(Level.SEVERE, "Error en el cliente", e);
            }
        } catch (IOException | GeneralSecurityException e) {
            logger.log(Level.SEVERE, "Error al iniciar el cliente", e);
        }
    }
}