import socket

IP = "myctf-env.eba-bd2y2npx.eu-west-2.elasticbeanstalk.com"
PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_STREAM) # UDP
sock.bind((IP, PORT))

sock.listen(0)

client_socket, client_address = sock.accept()
print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

client_socket.send("hello".encode("utf-8"))

client_socket.close()

sock.close()
