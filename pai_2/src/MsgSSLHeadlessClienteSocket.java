import java.io.*;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.util.Scanner;
import java.util.logging.*;
import javax.net.ssl.*;


public class MsgSSLHeadlessClienteSocket {

    private static final Logger logger = Logger.getLogger(MsgSSLHeadlessClienteSocket.class.getName());

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
        try (Scanner scanner = new Scanner(System.in)) {
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
            try (SSLSocket socket = (SSLSocket) factory.createSocket("server-0", 3343);
                 PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()), true);
                 BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {

                // Validación de nombre de usuario
                String username = null;
                while (username == null || username.trim().isEmpty()) {
                    System.out.print("Ingrese su nombre de usuario: ");
                    username = scanner.nextLine();
                    if (username == null || username.trim().isEmpty()) {
                        System.out.println("El nombre de usuario no puede estar vacío.");
                    }
                }

                // Validación de contraseña
                Console console = System.console();
                String password = null;

                if (console != null) {
                    char[] passwordArray = console.readPassword("Ingrese su contraseña: ");
                    password = new String(passwordArray);
                } else {
                    System.out.print("Ingrese su contraseña: ");
                    password = scanner.nextLine();  // Para entornos donde no hay consola real
                }

                if (password == null || password.trim().isEmpty()) {
                    System.out.println("La contraseña no puede estar vacía.");
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
                            System.out.print("Ingrese el usuario destino: ");
                            destinationUser = scanner.nextLine();
                            if (destinationUser == null || destinationUser.trim().isEmpty()) {
                                System.out.println("El usuario destino no puede estar vacío.");
                            }
                        }

                        // Enviar solicitud de verificación de usuario destino
                        output.println("VERIFY_USER:" + destinationUser);
                        response = input.readLine();

                        if ("Usuario existe".equals(response)) {
                            System.out.println("El usuario destino es válido.");
                            validUser = true;
                        } else if ("Usuario no existe".equals(response)) {
                            System.out.println("El usuario destino no existe. Por favor, inténtelo de nuevo.");
                            destinationUser = null; // Reiniciar el valor del usuario destino
                        } else {
                            System.out.println("Error en la verificación. Cerrando cliente.");
                            break;
                        }
                    }

                    // Validación del mensaje
                    String messageContent = null;
                    while (messageContent == null || messageContent.trim().isEmpty()) {
                        System.out.print("Ingrese su mensaje: ");
                        messageContent = scanner.nextLine();
                        if (messageContent == null || messageContent.trim().isEmpty()) {
                            System.out.println("El mensaje no puede estar vacío.");
                        }
                    }

                    // Enviar mensaje al servidor
                    output.println("MENSAJE:" + username + ":" + destinationUser + ":" + messageContent);
                    response = input.readLine();
                    System.out.println("Respuesta del servidor: " + response);

                } else {
                    System.out.println("Autenticación fallida. Cerrando cliente.");
                }

            } catch (IOException e) {
                logger.log(Level.SEVERE, "Error en la conexión del cliente", e);
            }
        } catch (IOException | GeneralSecurityException e) {
            logger.log(Level.SEVERE, "Error al iniciar el cliente", e);
        }
    }
}
