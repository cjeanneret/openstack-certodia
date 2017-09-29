# Code is mainly taken from those two files:
# https://github.com/certbot/certbot/blob/master/acme/examples/example_client.py
# https://github.com/letsencrypt/boulder/blob/master/test/chisel.py
#

import haproxy
import socket
import subprocess
import tools


class certbot():
    def __init__(self, config, logger):
        self.__config = config
        self.__webroot = '/var/www'
        self.__logger = logger
        self.__haproxy = haproxy(logger)

    def __deactivate(self):
        '''
        Small helper: deactivate all backend but the one we're on
        '''
        backends = self.__haproxy.get_backends('horizon')
        current_name = socket.gethostname()
        for backend in backends:
            if backend != current_name:
                self.__haproxy.disable_backend(backend)

    def __activate(self):
        '''
        Activate all backends without any filter
        '''
        backends = self.__haproxy.get_backends('horizon')
        for backend in backends:
            self.__haproxy.enable_backend(backend)

    def __exec(self, cmd):
        '''
        Small wrapper that logs commands to syslog
        '''
        ps = subprocess.Popen(
                cmd.split(),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE
                )
        process_output, _ = ps.communicate()
        self.__logger.info(process_output)

    def register(self):
        '''
        Register client to ACME
        '''
        cmd = 'certbot register -m %s --no-eff-email --agree-tos'
        self.__exec(cmd % self.__config['email'])

    def create(self):
        '''
        Create brand new certificate
        in case nothing is present on host.
        '''
        if tools.check_port(80):
            cmd = 'certbot certonly -n --agree-tos -d %s --webroot --webroot-path %s' % ( # noqa
                    self.__config['clouddomain'], self.__webroot) # noqa
        else:
            cmd = 'certbot certonly -n --agree-tos -d %s --standalone'
        self.__exec(cmd)

    def renew(self):
        '''
        Try to renew certificate on host if
        certificate is already present.
        This method will also take care of the haproxy
        backend management as well as reload
        '''
        cmd = 'certbot renew --agree-tos'
        self.__exec(cmd)
