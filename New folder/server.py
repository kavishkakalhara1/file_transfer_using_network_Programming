import socket
import threading

# Server Configuration
SERVER_HOST = "192.168.8.163"
SERVER_PORT = 5005
BUFFER_SIZE = 4096
clients = {}  # Dictionary to store connected clients


def handle_client(client_socket, client_address):
    client_name = None
    try:
        # Receive the client name and add to the client list
        client_name = client_socket.recv(BUFFER_SIZE).decode()
        if not client_name:
            return

        clients[client_name] = client_socket
        client_socket.send("ACK".encode())  # Acknowledge client connection
        print(f"{client_name} connected from {client_address}")

        # Notify all clients about the updated list
        broadcast_client_list()

        while True:
            # Handle incoming data from the client
            data = client_socket.recv(BUFFER_SIZE).decode()
            if not data:
                break

            command, *args = data.split('|')

            if command == "SEND":
                handle_file_transfer(client_name, client_socket, args)

    except Exception as e:
        print(f"Error with {client_address}: {e}")

    finally:
        if client_name in clients:
            del clients[client_name]
        client_socket.close()
        # Notify all clients about the updated list after client disconnects
        broadcast_client_list()


def broadcast_client_list():
    try:
        client_list = "|".join(clients.keys())  # Create the updated list

        for client_socket in clients.values():
            try:
                client_socket.send(f"CLIENT_LIST_UPDATE|{client_list}".encode())
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
    except Exception as e:
        print(f"Error broadcasting client list: {e}")


def handle_file_transfer(sender_name, sender_socket, args):
    """Handles file transfer between clients."""
    try:
        if len(args) < 3:
            sender_socket.send("ERROR|Invalid file transfer request".encode())
            return

        target_client, filename, file_size = args[0], args[1], int(args[2])

        if target_client not in clients:
            sender_socket.send("ERROR|Target client not found".encode())
            return

        receiver_socket = clients[target_client]
        receiver_socket.send(f"RECEIVE|{sender_name}|{filename}|{file_size}".encode())

        bytes_forwarded = 0
        while bytes_forwarded < file_size:
            chunk = sender_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            receiver_socket.send(chunk)
            bytes_forwarded += len(chunk)

        print(f"File '{filename}' sent from {sender_name} to {target_client}")

    except Exception as e:
        print(f"File transfer error: {e}")
        sender_socket.send("ERROR|File transfer failed".encode())


def start_server():
    """Start the server and handle incoming client connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", SERVER_PORT))
    server.listen(5)
    print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


if __name__ == "__main__":
    start_server()
