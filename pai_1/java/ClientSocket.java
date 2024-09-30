import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;

import javax.swing.JOptionPane;

public class ClientSocket {

	/**
	 * @param args
	 * @throws IOException
	 */
	public static void main(String[] args) throws IOException {
	try {

		// create Socket from factory
		Socket socket = new Socket("127.0.0.1", 3343);

		// create PrintWriter for sending login to server
		PrintWriter output = new PrintWriter(new OutputStreamWriter(
					socket.getOutputStream()));
		// prompt user for user name
		String userName = JOptionPane.showInputDialog(null,
					"Enter User Name:");

		// send user name to server
		output.println(userName);

		// prompt user for password
		String password = JOptionPane.showInputDialog(null,
					"Enter Password:");

		// send password to server
		output.println(password);

		output.flush();

		// create BufferedReader for reading server response
		BufferedReader input = new BufferedReader(new InputStreamReader(
					socket.getInputStream()));

		// read response from server
		String response = input.readLine();

		// display response to user
		JOptionPane.showMessageDialog(null, response);

		// clean up streams and Socket
		output.close();
		input.close();
		socket.close();

	} // end try

	// handle exception communicating with server
	catch (IOException ioException) {
		ioException.printStackTrace();
	}

	// exit application
	finally {
		System.exit(0);
	}
 
    }
}
