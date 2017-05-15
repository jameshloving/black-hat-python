#!/bin/python

import sys
import socket
import getopt
import threading
import subprocess

# why do we need so many variables???
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0

'''
    Print the usage instructions
'''
def usage():

    print('BHP Net Tool\n')
    print('Usage: bhpnet.py -t target -p port')
    print('-l --listen          listen on [host]:[port]')
    print('                     for incoming connections')
    print('-e --execute=file    execute the given file upon')
    print('                     receiving a connection')
    print('-c --command         initialize a command shell')
    print('-u --upload=dest     upon receiving connection,')
    print('                     upload a file to [dest]\n\n')

    sys.exit(0)



'''
    Send data to another host over TCP
'''
def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while 1:
            recv_len = 1
            response = ''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            
            print(response)

            buffer = raw_input('')
            buffer += '\n'

            client.send(buffer)

    except:
        print('*** Exception! Exiting.')
        # this exception is being thrown on the execution from bottom of p19
        client.close()



def server_loop():
    
    global target

    # if no specific target, listen to all interfaces
    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while 1:
        (client_socket, address) = server.accept()

        client_thread = threading.Thread(target = client_handler,
                                         args = (client_socket, ))
        client_thread.start()



'''
    Run a command locally and return the output
'''
def run_command(command):

    command = command.rstrip()

    try:
        output = subprocess.check_output(command,
                                         stderr = subprocess.STDOUT,
                                         shell = True)
    except:
        output = 'Failed to execute command.'

    return output



'''
    Handle client-side functionality
'''
def client_handler(client_socket):

    global upload
    global execute
    global command

    # handle uploads
    if len(upload_destination):
        file_buffer = ''

        while 1:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            with open(upload_destination, 'wb') as f:
                f.write(file_buffer)
            
            client_socket.send('Successfully saved file to {0}\n'.format(upload_destination))

        except:
            client_socket.send('Failed to save file to {0}\n'.format(upload_destination))

    if len(execute):
        output = run_command(execute)

        client_socket.send(output)

    if command:
        while 1:
            client_socket.send('<BHP:#> ')

            cmd_buffer = ''

            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)

            client_socket.send(response)



'''
    Core functionality
'''
def main():

    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    # print usage if there aren't CLI arguments
    if not len(sys.argv[1:]):
        usage()

    try:
        (opts, args) = getopt.getopt(sys.argv[1:],
                                     'hle:t:p:cu:',
                                     ['help', 'listen', 'execute', 'target', 'port', 'command', 'upload'])
    except getopt.GetoptError as err:
        print(str(err))
        usage() 

    for (o, a) in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-e', '--execute'):
            execute = a
        elif o in ('-c', '--command'): # BHP is incorrect, has this as --commandshell
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            assert (False, "Unhandled Option") # is this appropriate? doesn't re-print usage()

    # send data from stdin when appropriate
    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()



if __name__ == '__main__':
    main()
        
