import base64
import socket
import ssl
import configparser

config = configparser.ConfigParser()
config.read("message/setting.ini")

addresses = config.get("Settings", "Recievers").split(',')
theme = config.get("Settings", 'Theme')

attachments = config.get("Settings", "Attachments").split(',')
if '' in attachments:
    attachments.remove('')

message = ''
with open ('message/message.txt', 'r') as f:
    for line in f:
        message += line

class UnsupportedTypeError(Exception):
    pass

def get_type(type):
    if type == 'jpeg' or type =='jpg':
        return 'image/jpeg;'
    elif type == 'png':
        return 'image/png;'
    elif type == 'pdf':
        return 'application/pdf;'
    elif type == 'zip':
        return 'application/zip;'
    else:
        raise UnsupportedTypeError()



def code_file_base64(a):
    with open ('message/'+a, 'br') as f:
        return base64.b64encode(f.read())


def form_message(theme, addresses, message, attachmenets):
    text =""
    text += "From: Katy Solo (test.katy.solo@yandex.ru)\n"
    text += "To: " + ','.join(addresses) + '\n'
    text += "Subject: " + '=?UTF-8?B?'+base64.b64encode(theme.encode()).decode()+'?=' +'\n'
    if attachments:
        text += "Content-Type: multipart/mixed; boundary = +++\n\n\n"
        if message:
            text += '--+++\n'
            text += 'Content-Type: text/plain; charset=utf-8\n\n'
            text += message
        for a in attachments:
            name_base64 = '"=?UTF-8?B?'+base64.b64encode(a.encode()).decode()+'?="'
            text += '--+++\n'
            text += 'Content-Disposition: attachment; filename='+name_base64+'\n'
            text += 'Content-Transfer-Encoding: base64\n'
            text += "Content-Type: " + get_type(a.split('.')[1]) + ' name='+ name_base64+'\n\n'
            text += code_file_base64(a).decode() + '\n'
        text += '--+++--'
    else:
        text += 'Content-Type: text/plain; charset=utf-8\n\n'
        text += message
    return text + '\n.'

input_lines = ['EHLO hackerman.ru', 'AUTH LOGIN',
               base64.b64encode('test.katy.solo@yandex.ru'.encode()).decode(),
               base64.b64encode('qwertyKate98'.encode()).decode(),
               'MAIL FROM: test.katy.solo@yandex.ru',
               'RCPT TO: colo18@yandex.ru',
               'RCPT TO: test.katy.solo@yandex.ru',
               'DATA',
                form_message(theme,addresses,message,attachments),
               'QUIT'
               ]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('smtp.yandex.ru', 465))
ssl_sock = ssl.wrap_socket(sock)
data = ssl_sock.recv(1024)
print(data.decode())
for i in input_lines:
    ssl_sock.send((i + '\r\n').encode())
    data = ssl_sock.recv(1024)
    print(data.decode())
ssl_sock.close()
