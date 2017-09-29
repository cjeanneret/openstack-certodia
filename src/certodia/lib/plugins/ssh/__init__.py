# ssh backend plugin
import argparse
import os
import paramiko
import socket


class Client:
    def __init__(self, logger):

        self.__logger = logger
        self.__args = None
        self.__user = None
        self.__ssh_key = None
        self.__transport = None
        self.__sftp_client = None
        self.__clouddomain = ''


    def __sftp(self):
        if self.__check_remote():
            self.__logger.info('Connecting to %s' % self.__clouddomain)
            transport = paramiko.Transport((self.__clouddomain, 22))
            transport.settimeout(5)
            transport.auth_publickey(self.__user, self.__ssh_key)
            self.__sftp_client = paramiko.SFTPClient.from_transport(transport)
        else:
            self.__logger.info('Remote host %s not reachable' % self.__clouddomain)

    def __check_remote(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.__clouddomain, 22))
        except socket.error as e:
            return False
        s.close()
        return True

    def __get(self, fpath):
        fhandle = self.__sftp_client.file(fpath, 'r')
        return '\n'.join(fhandle.readlines())

    def __close(self):
        self.__sftp_client.close()
        self.__transport.close()

    def build_parser(self, parser):
        parser.add_argument('--ssh-user',
                            help='''SSH User to be used,
                            defaults to "root"''',
                            default='root')
        parser.add_argument('--ssh-key',
                            help='''SSH private key to be used,
                            defaults to "~/.ssh/id_rsa"''',
                            default=os.path.expanduser('~/.ssh/id_rsa'))
        return parser

    def config(self, conf):
        self.__logger.info('Merging configuration')
        self.__user = conf['SshUser']
        self.__ssh_key = conf['SshKey']
        self.__clouddomain = conf['Clouddomain']

    def fetch(self):
        if self.__sftp():
            base = os.path.join(
                    '/etc/letsencrypt/live',
                    self.__clouddomain,
                    )
            cert = self.__get(os.path.join(base, 'cert.pem'))
            chain = self.__get(os.path.join(base, 'chain.pem'))
            key = self.__get(os.path.join(base, 'privkey.pem'))
            self.__close()
            return (cert, chain, key)
        else:
            return False

    def push(self, local_file):
        return True
