import socket
import selectors
import types


IP ="0.0.0.0"
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
"jpg\n",
"File 2\n",
"File 3\n",
"File 1\n",
"File 5\n",
"File 5\n",
"File 4\n",
"$^^GMw08%fDPK*ga\n"
]

userAnswers={}

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
            if recv_data.decode("utf-8")==questionAnswers[len(userAnswers[key.data.addr[1]])]:
                userAnswers[key.data.addr[1]].append(True)
            else:
                userAnswers[key.data.addr[1]].append(False)
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            userAnswers.pop(key.data.addr[1])
            sock.close()

    if mask & selectors.EVENT_WRITE:
            try:
                if key.data.addr[1] not in userAnswers:
                    userAnswers[key.data.addr[1]] = []
                    sock.send(questions[len(userAnswers[key.data.addr[1]])].encode("utf-8"))
                
                if len(userAnswers[key.data.addr[1]])>=8:
                    if False in userAnswers[key.data.addr[1]]:
                        sock.send("You've got something wrong there. Try that again".encode("utf-8"))
                    else:
                        sock.send("!FLAG!{G00d_met4data_f0rens1cs}!FLAG!".encode("utf-8"))
                        
                    print(f"Closing connection to {data.addr}")
                    sel.unregister(sock)
                    userAnswers.pop(key.data.addr[1])
                    sock.close()
                else:
                    if data.outb:
                        print(f"Echoing {data.outb!r} to {data.addr}")
                        sent = sock.send(data.outb) 
                        data.outb = data.outb[sent:]
                        sock.send(questions[len(userAnswers[key.data.addr[1]])].encode("utf-8"))
            except:
                print(f"Closing connection to {data.addr}")
                userAnswers.pop(key.data.addr[1])  

sel = selectors.DefaultSelector()

sock.listen()
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()





    

