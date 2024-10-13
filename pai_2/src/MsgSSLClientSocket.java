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

            // Cargar el truststore
            String trustStorePath = "truststore.jks"; // Ruta al truststore
            String trustStorePassword = "trustpassword"; // Cambia por tu contraseña

            KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
            try (FileInputStream trustStoreStream = new FileInputStream(trustStorePath)) {
                trustStore.load(trustStoreStream, trustStorePassword.toCharArray());
            }

            SSLContext sslContext = SSLContext.getInstance("TLSv1.3"); // Asegúrate de usar TLS 1.3
            TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStore);
            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            keyManagerFactory.init(keyStore, keyStorePassword.toCharArray());
            sslContext.init(keyManagerFactory.getKeyManagers(), trustManagerFactory.getTrustManagers(), null);

            SSLSocketFactory factory = sslContext.getSocketFactory();
            SSLSocket socket = (SSLSocket) factory.createSocket("localhost", 3343);

            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()), true);

            boolean authenticated = false;

            // Bucle para manejar la autenticación
            while (!authenticated) {
                // Leer credenciales del usuario
                String username = JOptionPane.showInputDialog("Ingresa tu nombre y apellidos:");
                String password = JOptionPane.showInputDialog("Ingresa tu contraseña:");

                // Enviar credenciales al servidor
                output.println("CREDENTIALS:" + username + ":" + password);

                // Leer respuesta del servidor
                String response = input.readLine();
                JOptionPane.showMessageDialog(null, response);

                if (response != null && response.equals("Autenticación exitosa.")) {
                    authenticated = true; // Cambia el estado a autenticado

                    // Leer el usuario destino
                    String destinationUser = JOptionPane.showInputDialog("Ingresa el usuario destino:");

                    String message;
                    // Bucle para pedir el mensaje hasta que no esté vacío
                    do {
                        message = JOptionPane.showInputDialog("Ingresa tu mensaje:");
                        if (message == null || message.trim().isEmpty()) {
                            JOptionPane.showMessageDialog(null, "Mensaje vacío, por favor intenta de nuevo.");
                        }
                    } while (message == null || message.trim().isEmpty());

                    // Enviar el mensaje al servidor con el formato: "MENSAJE:usuarioFuente:usuarioDestino:mensaje"
                    output.println("MENSAJE:" + username + ":" + destinationUser + ":" + message); 
                    
                    // Leer respuesta del servidor sobre el mensaje
                    String messageResponse = input.readLine();
                    JOptionPane.showMessageDialog(null, messageResponse);
                } else {
                    // Si la autenticación falla, se cierra la conexión
                    JOptionPane.showMessageDialog(null, "La autenticación falló. Cerrando la conexión.");
                    break; 
                }
            }

            socket.close();
        } catch (IOException | GeneralSecurityException e) {
            logger.log(Level.SEVERE, "Error en el cliente", e);
            JOptionPane.showMessageDialog(null, "Error en la conexión: " + e.getMessage());
        }
    }
}