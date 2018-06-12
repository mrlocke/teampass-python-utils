# Title       : pssh.py
# Date        : Sat Jun  9 22:03:07 CEST 2018
# Author      : Jose Andres Arias Velichko <a.arias@.paislinux.es>
# Version     : See bellow "_version_" line
# Copyright   : 2018 Jose Andres Arias Velichko
# License     : GNU GPL-2.0
# Description : Password change library for linux hosts using ssh and expect
#
#  * This software is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
_version_ = '0.10.dev10'


from pexpect import pxssh
import sys

# My Error Classes
class PsshConnect(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PsshSudoError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class host:
    def __init__(self, host, port, user, pw):
        self.hostname = host
        self.port = port
        self.user = user
        self.pw = pw
        self.logfile = open(('/tmp/' + user + '@' + host + '.log'),'wb')
        self.__connection = pxssh.pxssh(options={
                                "StrictHostKeyChecking": "no",
                                "PubkeyAuthentication": "no",
                                "UserKnownHostsFile": "/dev/null"},
                                logfile=self.logfile)
        self.connect()

    def connect(self):
        self.__connection.force_password = True
        try:
            self.__connection.login(server=self.hostname, port=self.port,
                    username=self.user, password=self.pw)
            self.__connection.sendline('set +o history')
            self.__connection.prompt()
        except pxssh.ExceptionPxssh as detail:
            raise PsshConnect(detail)

    def close(self):
        self.__connection.logout()
        self.logfile.close()

    def host_info(self):
        self.__connection.sendline('echo "RESULTS,$USER@$HOSTNAME,$(lsb_release -s -i),$(lsb_release -s -r)"')
        self.__connection.prompt()
        print (self.__connection.before.decode("utf-8").splitlines()[-1])

    def sudo(self, pw):
        self.__connection.sendline('sudo -i')
        status = self.__connection.expect([pxssh.TIMEOUT,'password for','[\#\$] '])
        if status == 0:
            sys.stderr.write('Estamos en 0')
            sys.stderr.flush()
            raise PsshSudoError('Sudo timeout')
        if status == 1:
            sys.stderr.write('Estamos en 1')
            sys.stderr.flush()
            self.__connection.sendline(pw)
            status = self.__connection.expect([pxssh.TIMEOUT,'[\#\$] '])
            if status == 0:
                raise PsshSudoError('Sudo wrong password')
            self.__connection.set_unique_prompt()
        if status == 2:
            sys.stderr.write('Estamos en 2')
            sys.stderr.flush()
            self.__connection.set_unique_prompt()
        self.__connection.prompt()
        self.__connection.sendline('set +o history')
        self.__connection.prompt()
    
    def sudo_logout(self):
        self.__connection.sendline('logout')
        self.__connection.prompt()

  
# Plugin initialization functions
def ssh_plugin(main_host_data, additional_host_data = {}):
    '''Main function for ssh_plugin'''
    try:
        myhost = host(host=main_host_data["host"],
                user=main_host_data["user"],
                port=main_host_data["port"],
                pw=main_host_data["pw"])
        myhost.host_info()
        myhost.close()
        del myhost
    except PsshConnect:
        print ("Connection error")

    return False

def ssh_sudo_plugin(main_host_data, additional_host_data = {}):
    '''Main function for ssh_sudo_plugin'''
    try:
        myhost = host(host=additional_host_data["host"],
                user=additional_host_data["user"],
                port=additional_host_data["port"],
                pw=additional_host_data["pw"])
        myhost.sudo(additional_host_data["pw"])
        myhost.host_info()
        myhost.sudo_logout()
        myhost.close()
        del myhost
    except PsshConnect:
        print ("Connection error")

    return False
