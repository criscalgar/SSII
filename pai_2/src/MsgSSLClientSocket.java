package src;

import java.io.*;
import java.security.KeyStore;
import javax.net.ssl.*;
import javax.swing.JOptionPane;
import java.util.Properties;

public class MsgSSLClientSocket {
    public static void main(String[] args) {
        try {
            // Cargar configuración segura desde un archivo de propiedades
            Properties props = new Properties();
            try (InputStream input = new FileInputStream("config.properties")) {
                props.load(input);
            }

            // Configurar keystore y truststore con rutas y contraseñas
            System.setProperty("javax.net.ssl.keyStore", props.getProperty("clientKeystorePath"));
            System.setProperty("javax.net.ssl.keyStorePassword", props.getProperty("clientKeystorePassword"));
            System.setProperty("javax.net.ssl.trustStore", props.getProperty("truststorePath"));
            System.setProperty("javax.net.ssl.trustStorePassword", props.getProperty("truststorePassword"));

            // Crear socket SSL
            SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
            try (SSLSocket socket = (SSLSocket) factory.createSocket("localhost", 3343);
                 BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                 PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()))) {

                socket.startHandshake();  // Autenticación mutua y establecimiento de canal seguro

                // Solicitar credenciales de usuario
                String username = JOptionPane.showInputDialog(null, "Enter your username:");
                String password = JOptionPane.showInputDialog(null, "Enter your password:");

                output.println(username);
                output.println(password);
                output.flush();

                // Leer la respuesta del servidor
                String response = input.readLine();
                JOptionPane.showMessageDialog(null, response);

                // Enviar mensaje
                String msg = JOptionPane.showInputDialog(null, "Enter a message to send:");
                output.println(msg);
                output.flush();

                response = input.readLine();
                JOptionPane.showMessageDialog(null, response);

            } catch (SSLException sslException) {
                System.err.println("SSL error occurred: " + sslException.getMessage());
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}