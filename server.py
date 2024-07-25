import socket
import threading

HOST = '127.0.0.1'
PORT = 5000
HEADER_SIZE = 10


class Server:
    def __init__(self):
        # Lista con los sockets de los clientes
        self.connections = []
        # Se establece el socket del servidor (socket, bind, listen)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite eliminar el error "socket already in use"
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.listen()


    def run(self):
        print("Servidor iniciado. Esperando conexiones...")
        while True:
            # Se aceptan las conexiones entrantes
            conn, addr = self.sock.accept()

            # Se levanta el thread de manejo de las conexiones entrantes
            th = threading.Thread(target=self.handler, args=(conn, addr), daemon=True)
            th.start()

            # Informa sobre la conexion entrante
            print(str(addr[0]) + ':' + str(addr[1]), "connected")

            # Se agrega el socket cliente a la lista de conexiones
            self.connections.append(conn)

    def handler(self, conn, addr):
        while True:
            # Si es que no hay problemas con la conexion del cliente...
            try:
                # Lee el encabezdo para el buffer y los datos entrantes
                data_header = conn.recv(HEADER_SIZE)
                data = conn.recv(int(data_header))
                if data.decode("utf-8") == "FINISH":
                    conn.close()
                else:
                    # Hace ub broadcast del dato entrante a los otros sockets
                    for connection in self.connections:
                        connection.send(data_header + data)

            # Si hay problemas con la conexion del cliente...
            except:
                # El cliente se ha desconectado. Informar y eliminar a conexionj
                print(str(addr[0]) + ':' + str(addr[1]), "disconnected")
                self.connections.remove(conn)
                conn.close()
                break


server = Server()
server.run()