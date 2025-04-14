import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Server Configuration
SERVER_HOST = "192.168.43.202"
SERVER_PORT = 5005
BUFFER_SIZE = 4096


class FileTransferClient:
    def __init__(self, master):
        self.filepath = None
        self.master = master
        self.master.title("File Transfer Client")
        self.master.geometry("550x550")
        self.master.configure(bg="#222831")

        # Initialize socket and set it to None for later connection
        self.client_socket = None

        # Styling
        style = ttk.Style()
        style.configure("TButton", padding=5, font=("Arial", 10, "bold"), background="#00ADB5")
        style.configure("TLabel", font=("Arial", 12), foreground="white", background="#222831")

        # UI Elements
        self.name_label = ttk.Label(master, text="Enter Your Name:")
        self.name_label.pack(pady=5)
        self.name_entry = ttk.Entry(master, font=("Arial", 12))
        self.name_entry.pack(pady=5)

        self.connect_button = ttk.Button(master, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=5)

        self.file_button = ttk.Button(master, text="Select File", command=self.select_file)
        self.file_button.pack(pady=5)

        self.target_label = ttk.Label(master, text="Target Client:")
        self.target_label.pack(pady=5)
        self.target_entry = ttk.Entry(master, font=("Arial", 12))
        self.target_entry.pack(pady=5)

        self.send_button = ttk.Button(master, text="Send File", command=self.send_file)
        self.send_button.pack(pady=5)

        # Text widget to display the client list
        self.client_list_text = tk.Text(master, height=8, width=40, font=("Arial", 12), bg="#333333", fg="white",
                                        wrap="word")
        self.client_list_text.pack(pady=10)

    def connect_to_server(self):
        name = self.name_entry.get().strip()

        if self.client_socket:
            messagebox.showinfo("Connection", f"Already connected as {name}")

        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return

        # Create the socket connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.client_socket.send(name.encode())  # Send name to server

            # Wait for server acknowledgment
            response = self.client_socket.recv(BUFFER_SIZE).decode()
            if response == "ACK":
                messagebox.showinfo("Connection", "Connected to Server")
                # Start listening for incoming data after successful connection
                self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
                self.receive_thread.start()
            else:
                messagebox.showerror("Error", "Server did not acknowledge connection")
                self.client_socket.close()
                self.client_socket = None

        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.client_socket = None

    def select_file(self):
        self.filepath = filedialog.askopenfilename()
        if self.filepath:
            messagebox.showinfo("File Selected", f"Selected {os.path.basename(self.filepath)}")

    def send_file(self):
        """Send selected file to a target client."""
        target = self.target_entry.get().strip()
        if not target or not self.filepath:
            messagebox.showerror("Error", "Select a file and enter a target client")
            return

        filename = os.path.basename(self.filepath)
        filesize = os.path.getsize(self.filepath)

        try:
            self.client_socket.send(f"SEND|{target}|{filename}|{filesize}".encode())

            with open(self.filepath, "rb") as f:
                while chunk := f.read(BUFFER_SIZE):
                    self.client_socket.send(chunk)

            messagebox.showinfo("Success", "File Sent Successfully")

        except Exception as e:
            messagebox.showerror("File Transfer Error", f"Error sending file: {e}")

    def receive_data(self):
        while True:
            if self.client_socket is None:
                print("Socket is not connected.")
                break  # Exit the loop if the socket is None (not connected)

            try:
                data = self.client_socket.recv(BUFFER_SIZE)

                if not data:
                    print("Connection closed by server.")
                    break  # Exit the loop if no data is received (connection closed)

                try:
                    text_data = data.decode('utf-8')  # Try to decode as UTF-8 for text messages
                    print(text_data)  # Debugging print

                    if text_data.startswith("CLIENT_LIST_UPDATE"):
                        # Extract clients list from the received message
                        clients = text_data.split("|")[1:]  # Skip the CLIENT_LIST_UPDATE header
                        print("Client List Received:", clients)
                        self.update_client_list(clients)

                    elif text_data.startswith("RECEIVE"):
                        # Handle file transfer (downloading a file from another client)
                        parts = text_data.split("|")

                        if len(parts) < 4:
                            print("Error: Malformed RECEIVE message:", text_data)
                            return

                        _, sender, filename, file_size = parts
                        try:
                            file_size = int(file_size)  # Ensure valid integer
                        except ValueError:
                            print("Error: Received invalid file size:", file_size)
                            return

                        save_path = f"received_{filename}"
                        with open(save_path, "wb") as f:
                            remaining_size = file_size
                            while remaining_size > 0:
                                chunk = self.client_socket.recv(min(BUFFER_SIZE, remaining_size))
                                if not chunk:
                                    break  # Connection closed
                                f.write(chunk)
                                remaining_size -= len(chunk)

                        messagebox.showinfo("File Received", f"Received {filename} from {sender}")

                except UnicodeDecodeError:
                    print("Received binary data instead of text. Ignoring decoding attempt.")
                    continue  # Ignore if it's binary data

            except Exception as e:
                print(f"Error receiving data: {e}")
                break  # Exit the loop in case of an error

    def update_client_list(self, clients):
        print(clients)
        self.client_list_text.delete(1.0, tk.END)  # Clear the current list
        if clients:
            self.client_list_text.insert(tk.END, f"Connected Clients:\n")
            for client in clients:
                self.client_list_text.insert(tk.END, f"{client}\n")
        else:
            self.client_list_text.insert(tk.END, "No Clients Connected")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferClient(root)
    root.mainloop()
