# FileTransfer-Chat-Network

A Multi-Threaded Chat/File Transfer tool from one computer to others on a common Network 
You can transfer any type of file.

## Requirements:

Ubuntu / other Linux-based distros
MacOS

## Steps:

Compile the folder named "actual"
Here go to folder "chat" for chatbox code or to folder "ftp" for file transfer code.
```
	gcc server.c -o server
	gcc client.c -o client
```
## Options:

To run chatbox code
```
	./client [PORT]
	./server [PORT]
```
each in different terminal windows.

To run file transfer code (default port : 9000) 
```
	./client
	./server
``` 
each in different terminal windows.

## Testing:

You can test the program without the need for another computer by being server and client at the same time.
Follow the similar procedure for files in test folder.
For file transfer run client and server from different locations.

### Note:

Make sure you run the server and client on the same port.
In file transfer program, the filename will be asked in the program, you need to give the file location with name.
At this time, you have to change the port numbers manually in ftp line no-34 in client.c and 82 line server.c
You also need to change the ip-address manually in chatbox code in line.no-27 in client.c 

### To be done:

More options.
Input of ip address and port numbers.
Option to close connections and quit.
Chat and file transfer in the same program.
 
