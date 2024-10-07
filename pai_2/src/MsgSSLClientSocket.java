package src;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import javax.net.ssl.*;
import javax.swing.JOptionPane;

public class MsgSSLClientSocket {
    public static void main(String[] args) {
        try {
            System.setProperty("javax.net.ssl.trustStore", "mykeystore.jks");
            System.setProperty("javax.net.ssl.trustStorePassword", "your_keystore_password");

            SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
            SSLSocket socket = (SSLSocket) factory.createSocket("localhost", 3343);
            socket.startHandshake();

            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()));

            String username = JOptionPane.showInputDialog(null, "Enter your username:");
            String password = JOptionPane.showInputDialog(null, "Enter your password:");

            output.println(username);
            output.println(password);
            output.flush();

            String response = input.readLine();
            JOptionPane.showMessageDialog(null, response);

            String msg = JOptionPane.showInputDialog(null, "Enter a message to send:");
            output.println(msg);
            output.flush();

            response = input.readLine();
            JOptionPane.showMessageDialog(null, response);

            output.close();
            input.close();
            socket.close();

        } catch (IOException ioException) {
            ioException.printStackTrace();
        } finally {
            System.exit(0);
        }
    }
}