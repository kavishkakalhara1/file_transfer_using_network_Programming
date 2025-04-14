# 📁 Peer-to-Peer File Transfer System (Python + Tkinter GUI)

A simple yet effective Python-based peer-to-peer file transfer system with a GUI interface. Clients can connect to a central server, view the list of active users, and send files to any other connected peer.

## ✨ Features

- 📡 Multi-client support via central server  
- 📜 Real-time client list updates  
- 📁 Send any type of file (images, videos, documents)  
- ✅ Transfer acknowledgment and file size validation  
- 🖥️ User-friendly GUI built using Tkinter  
- 🔒 Graceful client disconnection handling  

---

## 🏗️ Project Structure

```
.
├── server.py             # Handles client connections and file forwarding  
├── client_gui.py         # GUI client that sends/receives files  
├── README.md             # Full project documentation  
```

---

## 🧰 Technologies Used

- **Python 3**  
- **Socket Programming** for TCP communication  
- **Threading** for handling multiple clients  
- **Tkinter** for GUI (cross-platform built-in Python library)  
- **OS/FileDialog** for file selection and transfer  

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/peer-file-transfer.git
cd peer-file-transfer
```

### 2. Optional: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

> This app uses only built-in modules, so no additional packages are required.

---

## 🖥️ Start the Server

Start the server (required before any clients connect):

```bash
python server.py
```

> Default server IP: `0.0.0.0`  
> Default port: `5005`

You can change the `SERVER_HOST` and `SERVER_PORT` inside `server.py`.

---

## 👤 Launch the Client GUI

Open a new terminal window for each client and run:

```bash
python client_gui.py
```

Each client can:  
1. Enter a **unique name**  
2. Click **Connect**  
3. Select a file using **"Select File"**  
4. Enter a target client name  
5. Click **Send File**

Received files are stored in the same directory with the prefix: `received_`.

---

## 📦 Example Flow

1. Client A starts and connects with name **Alice**  
2. Client B connects with name **Bob**  
3. Alice selects a file and sends it to **Bob**  
4. Bob gets the file saved as `received_<filename>`

---

## 🧪 Testing Tips

✅ Run the server and multiple clients on the same machine using different terminal instances.  
✅ Try file transfers of various sizes and types (e.g., `.txt`, `.jpg`, `.mp4`)  
✅ Test disconnections and reconnects  
✅ Attempt sending to non-existent clients to check error handling  

---

## ⚙️ Configuration

You can modify the following in both `server.py` and `client_gui.py`:

```python
SERVER_HOST = "192.168.43.202"  # Replace with your local IP
SERVER_PORT = 5005
BUFFER_SIZE = 4096
```

---

## 📌 Notes

- **No encryption or authentication** is used — meant for LAN/local usage or demo purposes only.  
- If sending large files, ensure both sender and receiver stay connected for the full duration.  
- Server acts as a **forwarder** between sender and receiver; this is not direct P2P.  

---

## ❓ FAQs

**Q: Can I run this over the internet (WAN)?**  
A: Yes, but you must expose the server's port using port forwarding or run it on a cloud server (e.g., EC2).  

**Q: Can I package the client as an `.exe`?**  
A: Yes, use [`pyinstaller`](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile client_gui.py
```

**Q: Does it support simultaneous transfers?**  
A: Not yet. Currently, the server handles transfers one-by-one via socket forwarding.  

---

## 🛡️ Security Disclaimer

This is a basic educational/demo tool and **should not be used in production without:**
- TLS encryption
- Authentication and access control
- File integrity and size verification
- Transfer resumability

---

## 📄 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

---

## 👨‍💻 Author

Developed by [Kalhara](https://github.com/kavishkakalhara1)  
Faculty of Engineering, University of Ruhuna  
© 2025

---
