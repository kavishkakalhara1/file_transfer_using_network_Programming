### Server Code (server.py)
import socket
import threading

# Server Configuration
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
BUFFER_SIZE = 4096
clients = {}


def handle_client(client_socket, client_address):
    try:
        client_name = client_socket.recv(BUFFER_SIZE).decode()
        clients[client_name] = client_socket
        print(f"{client_name} connected from {client_address}")

        while True:
            data = client_socket.recv(BUFFER_SIZE).decode()
            if not data:
                break
            command, *args = data.split('|')

            if command == "LIST":
                client_list = "|".join(clients.keys())
                client_socket.send(client_list.encode())

            elif command == "SEND":
                target_client = args[0]
                filename = args[1]
                file_size = int(args[2])

                if target_client in clients:
                    clients[target_client].send(f"RECEIVE|{client_name}|{filename}|{file_size}".encode())

                    with open(f"received_{filename}", "wb") as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = client_socket.recv(BUFFER_SIZE)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)

                    print(f"File {filename} received and forwarded to {target_client}")
                else:
                    client_socket.send("ERROR|Client not found".encode())
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        del clients[client_name]


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


if __name__ == "__main__":
    start_server()