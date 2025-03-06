import socket

IP = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_STREAM) # UDP
sock.bind((IP, PORT))

questions=[
"\nWhat type of file are all the files (give file extension)?  ",
"\nWhich file is the original?  ",
"\nWhich file has been most recently accessed?  ",
"\nWhich file is an exact copy of the original?  ",
"\nWhich file has been moved into a different drive?  ",
"\nWhich file has been renamed?  ",
"\nWhich file is unrelated to the original?  ",
"\nWhat is my password I hid in the answer to the last question?  "
]
questionAnswers=[
"BMP\n",
"File 2\n",
"File 3\n",
"File 1\n",
"File 5\n",
"File 5\n",
"File 4\n",
"$^^GMw08%fDPK*ga\n"
]

while True:
    sock.listen(0)
    questionReponseBool=[]
    client_socket, client_address = sock.accept()
    client_socket.send("Help! I've gotten my files all confused. Please help me reorganise them answer my questions. I'll give you a flag if you help me fully. \n".encode("utf-8"))

    for i in range(len(questions)):
        client_socket.send(questions[i].encode("utf-8"))
        questionResponse=client_socket.recv(1024)
        questionResponse=questionResponse.decode("utf-8")

        if questionResponse==questionAnswers[i]:
            questionReponseBool.append(True)
        else:
            questionReponseBool.append(False)

    if False in questionReponseBool:
        client_socket.send("You've got something wrong there. Try that again".encode("utf-8"))
    else:
        client_socket.send("!FLAG!{G00d_met4data_f0rens1cs}!FLAG!".encode("utf-8"))
    client_socket.close()




    

