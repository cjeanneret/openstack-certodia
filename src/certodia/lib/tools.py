import hashlib
import netifaces
import os
import psutil
import socket
import imp
from OpenSSL import crypto


def load_plugin(plugins, plugin):
    p = (item for item in plugins if item["name"] == plugin).next()
    return imp.load_module('__init__', *p["info"])


def get_plugins():
    plugins = []
    d = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(d, 'plugins')
    possiblePlugins = os.listdir(d)
    for i in possiblePlugins:
        location = os.path.join(d, i)
        if (not os.path.isdir(location)
                or '__init__.py' not in os.listdir(location)):
            continue
        info = imp.find_module('__init__', [location])
        plugins.append({"name": i, "info": info})

    return plugins


def compare_certs(buffer1, buffer2):
    '''
    Using OpenSSL.crypto, compare two certificate
    content based on certificate serial number.
    '''
    cert1 = crypto.load_certificate(crypto.FILETYPE_PEM, buffer1)
    cert2 = crypto.load_certificate(crypto.FILETYPE_PEM, buffer2)

    serial1 = cert1.get_serial_number()
    serial2 = cert2.get_serial_number()

    return (serial1 == serial2)


def check_hash(file1, file2):
    '''
    Return True if files match.
    False if not or if one of the file does
    not exist.
    '''
    if not os.path.exists(file1):
        return False
    if not os.path.exists(file2):
        return False

    with open(file1, 'r') as f:
        chk1 = hashlib.sha256(f.read()).hexdigest()
    with open(file2, 'r') as f:
        chk2 = hashlib.sha256(f.read()).hexdigest()

    return(chk1 == chk2)


def is_master(domain):
    '''
    Checks if the VIP is attached to the current host
    '''
    vip = socket.gethostbyname(domain)
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            if vip in [addr['addr'] for addr in addrs[netifaces.AF_INET]]:
                return True
    return False


def check_port(port):
    '''
    Check if <port> is free or already taken by a process
    '''
    ports = psutil.net_connections()
    for p in ports:
        if port.laddr[1] == port:
            return True
    return False


def create_bundle(domain, bundle):
    '''
    Creates PEM bundle for HAProxy
    A bundle consists in the following files:
    - cert
    - chain
    - private key
    In our case we will use the fullchain provided by certbot
    '''
    p = os.path.join('/etc/letsencrypt/live', domain)
    with open(bundle, 'w+') as f:
        f.write(open(os.path.join(p, 'fullchain.pem')).read())
        f.write(open(os.path.join(p, 'privkey.pem')).read())
