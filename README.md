# Reliable UDP Client-Server System
## CS176A Computer Communication Networks Assignment

The basic functionality of the system is to exchange commands and output between a client and server. The client and server should be run on different machines or different directories on the same machine.

The client, when started, requests the following information:
1. Enter server name or IP address:
2. Enter port:
3. Enter command:

The client, then, will try to connect to the specified server on the specified port and transmit the command.

### The general interaction between the client and server is as follows:
1. The server starts and waits for a connection to be established by the client.
2. When a command is received, then the server will:
  * Issue the command to its system and store the output in a file.
  * Open the file, read its content to a buffer.
  * Write the buffer contents to the connection established by the client.
3. The client will receive the data from the socket and store it in a local file.

### Detailed operation:
1. The client will format the command to be executed and send the length of the string to the server (a "length" message). Then, in a separate message, it will send the command string.
2. When the server receives the length message it will wait up to 500 milliseconds for that number of bytes to be sent. If it receives the correct number of bytes, it will respond with a string containing the characters "ACK" (an "acknowledgement"). If it does not receive the correct number of bytes by the end of the timeout period, it will give up on this message and issue a message informing the user that obtaining instructions failed. This message should be in the format "Failed to receive instructions from the client." After that the server should remain idle, waiting for another length message to be sent. If you have a large file that is divided into segments, every segment must be ACKed in order to preserve the stop-n-wait characteristics of the protocol.
3. If your client has not received an ACK within 1 second it will resend the length value and then the request message again.
4. Your client will resend, up to 3 times, before giving up, closing the connection and terminating. Upon closing connection, the client should display the following message: "Failed to send command. Terminating."
5. The server will implement reliability in a similar fashion. First, it will compute the size of the data it has to send and then will send it in a "length" message. The server will then send messages containing the output one by one and will wait for an ACK for each message sent and before the next, new message is sent. Similar to the client, the server will retry sending single message up to three times, before giving up. If the server does not receive an ACK message after three attempts, it should issue a message informing the user that output transmission failed. Use the format "File transmission failed."
6. Finally, upon successful reception of the output, the client should display the following message "File filename saved."
