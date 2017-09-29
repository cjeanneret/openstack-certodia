import argparse
import os
import requests


class Client:
    def __init__(self, logger):

        self.__logger = logger
        self.__args = None
        self.__cust_auth_key = None
        self.__cust_auth_id = None
        self.__cust_content_type = 'application/octet-stream'
        pass

    def __exists(self):
        '''
        Check whether object exists in remote storage
        '''
        exists = requests.get(
                self.__uri,
                headers=dict(
                    self.__auth_hd,
                    **self.__header_content_type
                    )
                )
        return (exists.status_code == 200)

    def __get(self):
        '''
        Get remote content
        '''
        resp = requests.get(
                self.__uri,
                headers=dict(
                    self.__cust_auth_hd,
                    **self.__header_content_type
                    )
                )
        if resp.status_code == 200:
            return resp.text
        return False

    def __put(self, container):
        '''
        Put or replace remote content
        '''
        # check if remote content exists
        if self.__exists():
            self.__delete()

        resp = requests.put(
                self.__uri,
                headers=dict(
                    self.__cust_auth_hd,
                    **self.__header_content_type
                    )
                )
        return (resp == 201)

    def __delete(self):
        '''
        Check if element exists and delete it
        '''
        if self.__exists():
            resp = requests.delete(
                    self.__uri,
                    headers=dict(
                        self.__cust_auth_hd,
                        **self.__header_content_type
                        )
                    )
            return (resp.status_code == 204)
        return True

    def build_parser(self, parser):
        parser.add_argument('--cust-auth-id',
                                   help='Custodia AUTH_ID for authentication')
        parser.add_argument('--cust-auth-key',
                                   help='Custodia AUTH_KEY for authentication')
        parser.add_argument('--cust-content-type',
                                   help='Custodia content type',
                                   default='application/octet-stream')
        parser.add_argument('--endpoint', '-E',
                                   help='Secure storage endpoint',
                                   required=True)


        return parser

    def config(self, conf):
        '''
        Configure the plugin specific options
        '''
        # We have a nice YAML
        self.__cust_auth_key = conf['CustAuthKey']
        self.__cust_auth_id = conf['CustAuthId']
        if 'ContentType' in conf:
            self.__cust_content_type = conf['CustContentType']

        self.__cust_auth_hd = {
                'CUSTODIA_AUTH_ID': self.__cust_auth_id,
                'CUSTODIA_AUTH_KEY': self.__cust_auth_key,
                }

    def fetch(self):
        '''
        Fetch secret from Custodia Container
        Returns, in that order: cert, chain and key
        '''

    def push(self, local_file):
        '''
        Push secret in Custodia Container
        '''
        filename = os.path.basename(local_file)
        self.__push(local_file, filename)
