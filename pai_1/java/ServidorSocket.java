import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;


public class ServidorSocket {
	
	/**
	 * @param args
	 * @throws IOException 
	 * @throws InterruptedException 
	 */
	public static void main(String[] args) throws IOException,          
                           InterruptedException {

		
		// perpetually listen for clients
		ServerSocket serverSocket = new ServerSocket(3343);
		while (true) {

		// wait for client connection and check login information
		try {
		System.err.println("Waiting for connection...");
						
		Socket socket = serverSocket.accept();

		// open BufferedReader for reading data from client
		BufferedReader input = new BufferedReader(new
                               InputStreamReader(socket.getInputStream()));

		// open PrintWriter for writing data to client
		PrintWriter output = new PrintWriter(new 
                    OutputStreamWriter(socket.getOutputStream()));
		String userName = input.readLine();
		String password = input.readLine();
		output.println("User, " + userName);
		output.println("Pass, " + password);
			

		output.close();
		input.close();
		socket.close();

		} // end try

		// handle exception communicating with client
		catch (IOException ioException) {
			ioException.printStackTrace();
		}

	} // end while

   }

}
