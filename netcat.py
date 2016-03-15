# -*-coding:utf8-*-
import sys
import socket
import getopt
import threading
import subprocess

# 全局变量

listen = False
command = False
upload = ''
execute = ''
target = ''
upload_destination = ''
port = 0


def usage():
    print("This is Usage")
    sys.exit(0);


def client_sendbuffer(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    try:
        client.connect((target, port));
        if len(buffer):
            client.send(buffer);
        while True:
            rec_len = 1;
            response = "";
            while rec_len:
                data = client.recv(4096);
                rec_len = len(data);
                response += data;
                if (rec_len < 4096):
                    break;
            print(response);
            buffer = raw_input("");
            buffer += "\n";
            client.send(buffer);
    except:
        print("handle error");
        client.close();


def server_loop():
    global target;
    if not len(target):
        target = "0.0.0.0";
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    print((target, port))
    server.bind((target, port));
    server.listen(5);

    while True:
        client, addr = server.accept();
        thread = threading.Thread(target=client_handler, args=(client,))
        thread.start();


def run_command(command):
    command = command.strip();
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True);
    except:
        output = "Fail to execute command\r\n";
    return output;


def client_handler(client):
    global upload_destination;
    global execute;
    global command;

    if len(upload_destination):
        fileBuffer = "";
        while True:
            data = client.recv(4096);
            if not data:
                break;
            else:
                fileBuffer += data;
        try:
            with open(upload_destination, 'wb') as f:
                f.write(fileBuffer);
            client.send("file has saved to %s" % upload_destination);
        except:
            client.send("fail to save file");
    if len(execute):
        output = run_command(execute);
        client.send(output);
    if command:
        while True:
            client.send("<BHP:#>");
            cmd_buffer = "";
            while "\n" not in cmd_buffer:
                cmd_buffer += client.recv(4096);
            response = run_command(cmd_buffer);
            client.send(response);


def main():
    global listen;
    global port;
    global execute;
    global command;
    global upload_destination;
    global target;
    # 判断是否有参数输入
    if not len(sys.argv[1:]):
        usage();
    # 读取命令
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"]);
    except getopt.GetoptError as err:
        print(err)
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage();
        elif o in ("-l", "--listen"):
            listen = True;
        elif o in ("-e", "--execute"):
            execute = a;
        elif o in ("-c", "--commandshell"):
            command = True;
        elif o in ("-u", "--upload"):
            upload_destination = a;
        elif o in ("-t", "--target"):
            target = a;
        elif o in ("-p", "--port"):
            port = int(a);
        else:
            assert False, "UnKnown Command";
    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read();
        client_sendbuffer(buffer);
    if listen:
        server_loop();


if (__name__ == "__main__"):
    main();
