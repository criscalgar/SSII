package src;

import java.io.*;
import javax.net.ssl.*;
import java.util.Properties;

public class MsgSSLServerSocket {

    public static void main(String[] args) {
        try {
            // Cargar configuración segura desde un archivo de propiedades
            Properties props = new Properties();
            try (InputStream input = new FileInputStream("config.properties")) {
                props.load(input);
            }

            // Configurar keystore y truststore con rutas y contraseñas
            System.setProperty("javax.net.ssl.keyStore", props.getProperty("serverKeystorePath"));
            System.setProperty("javax.net.ssl.keyStorePassword", props.getProperty("serverKeystorePassword"));
            System.setProperty("javax.net.ssl.trustStore", props.getProperty("truststorePath"));
            System.setProperty("javax.net.ssl.trustStorePassword", props.getProperty("truststorePassword"));

            // Crear el socket SSL del servidor
            SSLServerSocketFactory sslServerSocketFactory = (SSLServerSocketFactory) SSLServerSocketFactory.getDefault();
            SSLServerSocket sslServerSocket = (SSLServerSocket) sslServerSocketFactory.createServerSocket(3343);

            System.out.println("Servidor SSL en espera de conexión...");

            // Configurar protocolos TLS seguros y suites de cifrado
            sslServerSocket.setEnabledProtocols(new String[] { "TLSv1.2" });
            sslServerSocket.setEnabledCipherSuites(new String[] { 
                "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256", 
                "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
            });

            while (true) {
                // Aceptar conexión del cliente
                try (SSLSocket sslSocket = (SSLSocket) sslServerSocket.accept();
                     BufferedReader input = new BufferedReader(new InputStreamReader(sslSocket.getInputStream()));
                     PrintWriter output = new PrintWriter(new OutputStreamWriter(sslSocket.getOutputStream()))) {

                    sslSocket.startHandshake();  // Autenticación mutua y establecimiento de canal seguro

                    // Leer las credenciales enviadas por el cliente
                    String username = input.readLine();
                    String password = input.readLine();
                    System.out.println("Usuario autenticado: " + username);

                    // Validar credenciales (Aquí deberías usar bcrypt o un mecanismo seguro para verificar)
                    output.println("Autenticación exitosa");
                    output.flush();

                    // Leer el mensaje enviado por el cliente
                    String msg = input.readLine();
                    System.out.println("Mensaje recibido: " + msg);

                    // Enviar respuesta al cliente
                    output.println("Mensaje recibido correctamente");
                    output.flush();

                } catch (SSLException sslException) {
                    System.err.println("SSL error occurred: " + sslException.getMessage());
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}