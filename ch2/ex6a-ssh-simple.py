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
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))



ssh_command('192.168.1.45', 'jloving', 'password', 'whoami')
