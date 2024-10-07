package src;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import javax.net.ssl.*;

public class MsgSSLServerSocket {
    private static final String storedUsername = "user";
    private static final String storedPasswordHash = BCrypt.hashpw("pass", BCrypt.gensalt());

    public static void main(String[] args) {
        System.setProperty("javax.net.ssl.keyStore", "mykeystore.jks");
        System.setProperty("javax.net.ssl.keyStorePassword", "your_keystore_password");

        try {
            SSLServerSocketFactory factory = (SSLServerSocketFactory) SSLServerSocketFactory.getDefault();
            SSLServerSocket serverSocket = (SSLServerSocket) factory.createServerSocket(3343);

            System.err.println("Waiting for connection...");

            SSLSocket socket = (SSLSocket) serverSocket.accept();
            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()));

            String username = input.readLine();
            String password = input.readLine();

            if (storedUsername.equals(username) && BCrypt.checkpw(password, storedPasswordHash)) {
                output.println("Credentials accepted. Welcome to the server!");
            } else {
                output.println("Invalid credentials.");
            }
            output.flush();

            String msg = input.readLine();
            output.println("Server received: " + msg);
            output.flush();

            output.close();
            input.close();
            socket.close();

        } catch (IOException ioException) {
            ioException.printStackTrace();
        }
    }
}
