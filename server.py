import socket
import sys
from signal import SIGINT, SIGTERM, signal
from threading import Thread


def handle_signals():
    exit(1)


# used from previous part
def readConfirm(client, target):
    connected = True
    client.settimeout(10)
    msg = b""
    good_message = False
    while connected:
        try:
            msg += client.recv(1)
        except Exception:
            sys.stderr.write("ERROR:")
            connected = False
        if msg == target:
            connected = False
            good_message = True

    if good_message is False:
        raise Exception


# used from previous part
def readMsg(client, target, directory_path, id):
    full_path = directory_path + '/' + id + '.file'
    with open(full_path, 'wb') as file:
        try:
            readConfirm(client, b'confirm-accio\r\n')
            readConfirm(client, b'confirm-accio-again\r\n\r\n')
        except Exception:
            file.write(b'ERROR')
            client.close()
            return 0

        connected = True
        client.settimeout(10)
        msg = b""
        while connected:
            try:
                msg = client.recv(1024)
                file.write(msg)
            except Exception:
                file.seek(0)  # reset cursor
                file.truncate(0)  # delete file data so far so that we can write error
                file.write(b'ERROR')
                connected = False
            if msg == target:
                connected = False
        client.close()
        return 1


def main():
    port, directory = int(sys.argv[1]), sys.argv[2]
    socket_used = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_used.listen(15)
    socket_used.settimeout(10)
    try:
        socket_used.bind(("0.0.0.0", port))
    except Exception:
        sys.stderr.write('ERROR')
        exit(1)

    id = 0
    connected = True
    while connected:
        try:
            signal(SIGTERM, handle_signals)
            signal(SIGINT, handle_signals)
            (conn, addr) = socket_used.accept()
            current_thread = Thread(target=readMsg, args=(conn, b'', directory, id))
            current_thread.start()
            id = id + 1
        except Exception:
            id = id - 1
        id = id + 1

main()
