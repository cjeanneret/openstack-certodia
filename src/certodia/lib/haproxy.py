import csv
import os
import socket
import subprocess


class haproxy:
    def __init__(self, logger, socket='/var/lib/haproxy/stats'):
        self.__socket = socket
        self.__logger = logger
        self.__frontend = None
        self.__in_container = os.path.exists('/var/run/docker.sock')
        pass

    def __get_socket(self):
        '''
        Get a socket object (init connection and so on)
        '''
        if os.path.exists(self.__sock):
            s = socket.socket(
                    socket.AF_UNIX,
                    socket.SOCK_STREAM
                    )
            s.connect(self.__sock)
            s.setblocking(0)
            return s
        self.__logger.critical('Unable to get socket at "%s"' % self.__socket)
        return False

    def __send_sock_cmd(self, cmd):
        s = self.__get_sock()
        if s:
            s.sendall(cmd + "\n\n")
            f = s.makefile('r')
            lines = f.readlines()
            s.close()
            return lines
        self.__logger.critical(
                'Unable to send "%s" to socket "%s"' % (cmd, self.__socket)
                )
        return False

    def reload(self):
        '''
        Restart HAproxy iff
        - is active
        - config is OK
        Return True iff success
        False otherwise.
        '''
        if self.__in_container:
            self.__logger.info('Reloading haproxy container')
            # docker kill -s HUP $(docker ps -q --filter name=haproxy-bundle)
            get_haproxy = 'docker ps -q --filter name=haproxy-bundle'.split()
            container_id = subprocess.check_output(get_haproxy).rstrip()
            cmd = ('docker exe kill -s HUP %s' % container_id).split()
            return (subprocess.call(cmd) == 0)
        else:
            self.__logger.info('Reloading haproxy via systemctl')
            cmd = 'systemctl is-active haproxy'.split()
            is_active = subprocess.check_output(cmd).rstrip()

            if is_active == 'active':
                cmd = 'haproxy -q -c -f /etc/haproxy/haproxy.cfg'.split()
                if subprocess.call(cmd):
                    cmd = 'systemctl reload haproxy'.split()
                    return(subprocess.call(cmd) == 0)
            self.__logger.critical('Unable to reload HAProxy service')
            return False

    def disable_backend(self, server):
        '''
        Disable server in haproxy
        '''
        return self.__send_sock_cmd(
                'disable server %s/%s' % (self.__frontend, server)
                )

    def enable_backend(self, server):
        '''
        Enable server in haproxy
        '''
        return self.__send_sock_cmd(
                'enable server %s/%s' % (self.__frontend, server)
                )

    def get_backends(self, frontend):
        '''
        Get backends list for the selected frontend
        '''
        stats = self.__send_sock_cmd('/var/lib/haproxy/stats', 'show stat')
        self.__frontend = frontend
        if stats:
            backend = []
            backends = csv.reader(stats)
            for l in backends:
                if l[0] == frontend and l[1] not in ['FRONTEND', 'BACKEND']:
                    backend.append(l[1])
            return backend
        self.__logger.critical(
                'Unable to get backends for "%s" frontend' % frontend
                )
        return False
