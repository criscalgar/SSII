import javax.net.ssl.*;
import java.io.*;
import java.net.Socket;
import java.security.KeyStore;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class simulate_clients {

    public static void main(String[] args) {
        // Crear un pool de threads para ejecutar hasta 300 clientes concurrentemente
        ExecutorService executor = Executors.newFixedThreadPool(300);

        for (int i = 0; i < 300; i++) {
            final int clientId = i;
            executor.submit(() -> {
                try {
                    // Configurar SSL para el cliente
                    SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
                    TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
                    KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());

                    try (FileInputStream trustStoreStream = new FileInputStream("certs/truststore.jks")) {
                        trustStore.load(trustStoreStream, "trustpassword".toCharArray());
                    }
                    trustManagerFactory.init(trustStore);
                    sslContext.init(null, trustManagerFactory.getTrustManagers(), null);

                    SSLSocketFactory factory = sslContext.getSocketFactory();
                    SSLSocket socket = (SSLSocket) factory.createSocket("localhost", 3343);

                    // Enviar credenciales de prueba
                    try (BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                         BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {

                        out.write("CREDENTIALS:testuser:testpassword\n");
                        out.flush();

                        String response = in.readLine();
                        System.out.println("Cliente " + clientId + " - Respuesta del servidor: " + response);
                    }

                    socket.close();

                } catch (Exception e) {
                    System.err.println("Cliente " + clientId + " - Error: " + e.getMessage());
                }
            });
        }

        // Apagar el executor cuando termine
        executor.shutdown();
        while (!executor.isTerminated()) {
            // Espera a que todos los hilos terminen
        }

        System.out.println("Prueba de carga completada.");
    }
}