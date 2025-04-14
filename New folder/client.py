import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Server Configuration
SERVER_HOST = "192.168.164.207"
SERVER_PORT = 5005
BUFFER_SIZE = 4096

class FileTransferClient:
    def __init__(self, master):
        self.filepath = None
        self.master = master
        self.master.title("File Transfer Client")
        self.master.geometry("600x650")
        self.master.configure(bg="#2B2D42")  # Dark blue-gray background

        # Initialize socket
        self.client_socket = None

        # Styling
        style = ttk.Style()
        style.theme_use("clam")  # Modern theme
        style.configure("TButton", 
                       font=("Helvetica", 12, "bold"), 
                       padding=8, 
                       background="#4ECCA3",  # Teal button color
                       foreground="#FFFFFF")
        style.map("TButton", 
                 background=[("active", "#45B592")])  # Darker teal on hover
        style.configure("TLabel", 
                       font=("Helvetica", 14), 
                       foreground="#EDF2F4",  # Light gray text
                       background="#2B2D42")
        style.configure("TEntry", 
                       font=("Helvetica", 12), 
                       fieldbackground="#8D99AE")  # Light gray entry background

        # Header
        self.header = ttk.Label(master, text="File Transfer Client", font=("Helvetica", 20, "bold"))
        self.header.pack(pady=20)

        # Name Entry Frame
        self.name_frame = tk.Frame(master, bg="#2B2D42")
        self.name_frame.pack(pady=10, padx=20, fill="x")
        
        self.name_label = ttk.Label(self.name_frame, text="Your Name:")
        self.name_label.pack(side="left", padx=10)
        
        self.name_entry = ttk.Entry(self.name_frame, width=30)
        self.name_entry.pack(side="left", padx=10)

        # Connect Button
        self.connect_button = ttk.Button(master, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack(pady=15)

        # File Selection Frame
        self.file_frame = tk.Frame(master, bg="#2B2D42")
        self.file_frame.pack(pady=10, padx=20, fill="x")
        
        self.file_button = ttk.Button(self.file_frame, text="Select File", command=self.select_file)
        self.file_button.pack(side="left", padx=10)

        # Target Entry Frame
        self.target_frame = tk.Frame(master, bg="#2B2D42")
        self.target_frame.pack(pady=10, padx=20, fill="x")
        
        self.target_label = ttk.Label(self.target_frame, text="Target Client:")
        self.target_label.pack(side="left", padx=10)
        
        self.target_entry = ttk.Entry(self.target_frame, width=30)
        self.target_entry.pack(side="left", padx=10)

        # Send Button
        self.send_button = ttk.Button(master, text="Send File", command=self.send_file)
        self.send_button.pack(pady=15)

        # Client List
        self.client_list_label = ttk.Label(master, text="Connected Clients:", font=("Helvetica", 16))
        self.client_list_label.pack(pady=10)
        
        self.client_list_text = tk.Text(master, height=12, width=50, 
                                      font=("Helvetica", 12), 
                                      bg="#8D99AE",  # Light gray background
                                      fg="#2B2D42",  # Dark text
                                      relief="flat")
        self.client_list_text.pack(pady=10)

    def connect_to_server(self):
        name = self.name_entry.get().strip()

        if self.client_socket:
            messagebox.showinfo("Connection", f"Already connected as {name}")
            return

        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.client_socket.send(name.encode())
            response = self.client_socket.recv(BUFFER_SIZE).decode()
            
            if response == "ACK":
                messagebox.showinfo("Connection", "Connected to Server")
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
                break

            try:
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    print("Connection closed by server.")
                    break

                try:
                    text_data = data.decode('utf-8')
                    print(text_data)
                    if text_data.startswith("CLIENT_LIST_UPDATE"):
                        clients = text_data.split("|")[1:]
                        self.update_client_list(clients)
                    elif text_data.startswith("RECEIVE"):
                        _, sender, filename, file_size = text_data.split("|")
                        file_size = int(file_size)
                        save_path = f"received_{filename}"
                        with open(save_path, "wb") as f:
                            remaining_size = file_size
                            while remaining_size > 0:
                                chunk = self.client_socket.recv(min(BUFFER_SIZE, remaining_size))
                                if not chunk:
                                    break
                                f.write(chunk)
                                remaining_size -= len(chunk)
                        messagebox.showinfo("File Received", f"Received {filename} from {sender}")
                except UnicodeDecodeError:
                    print("Received binary data instead of text. Ignoring decoding attempt.")
                    continue

            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def update_client_list(self, clients):
        self.client_list_text.delete(1.0, tk.END)
        if clients:
            self.client_list_text.insert(tk.END, "Connected Clients:\n")
            for client in clients:
                self.client_list_text.insert(tk.END, f"{client}\n")
        else:
            self.client_list_text.insert(tk.END, "No Clients Connected")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferClient(root)
    root.mainloop()