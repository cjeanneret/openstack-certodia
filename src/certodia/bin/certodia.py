#!/usr/bin/env python

import argparse
import logging
import logging.handlers
import os
import sys
sys.path.append('../lib')
import config # noqa
import tools # noqa
import certbot # noqa
import haproxy # noqa


if __name__ == '__main__':
    LOG = logging.getLogger()
    LOG.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    LOG.addHandler(handler)
    plugins = tools.get_plugins()

    epilog = '''
Available plugins are: %s
    ''' % (', '.join([x['name'] for x in plugins]))

    parser = argparse.ArgumentParser(
            description='''
            Manage Let's Encrypt
            signed certificates and push/fetch
            them /tofrom a secure storage,
            like Custodia
            ''',
            epilog=epilog,
            prog=__file__,
            add_help=True,
            usage="%(prog)s PLUGIN [options|plugin options]")

    parser.add_argument('--clouddomain', '-C',
                        help='Cloud Domain',
                        required=True)
    parser.add_argument('--email', '-e',
                        help='''Let's Encrypt mail contact''',
                        required=True)
    parser.add_argument('--test', '-t',
                        help='''Request Let's Encrypt staging certificate''',
                        action='store_const',
                        const=True)
    parser.add_argument('--destination', '-d',
                        help='''Path to full bundle certificate''',
                        default='/etc/pki/tls/private/overcloud_endpoint.pem',
                        type=str)
    parser.add_argument('--config', '-c',
                        help='Configuration file (override all CLI args)')

    subparsers = parser.add_subparsers(
            title='Plugins',
            help='Plugin name',
            dest='plugin'
            )
    clients = {}
    plugin_parsers = {}
    for i in [x['name'] for x in plugins]:
        LOG.info('Loading %s' % i)
        clients[i] = tools.load_plugin(plugins, i)
        plugin_parsers[i] = subparsers.add_parser(i)
        pl = clients[i].Client(LOG)
        plugin_parsers[i] = pl.build_parser(plugin_parsers[i])

    args = parser.parse_args()

    client = clients[args.plugin].Client(LOG)

    conf = config.config(LOG, args).getConf()

    client.config(conf)

    # First fetch remote content if any
    # Please note the plugin MUST init the backend properly and do
    # all consistency checks by itself.
    try:
        cert, chain, key = client.fetch()
    except TypeError:
        LOG.info('Unable to fetch certificates - aborting')
        sys.exit(255)

    # flag: do we need to reload haproxy?
    reload_haproxy = False

    if tools.is_master(args.clouddomain):
        # We're on the master. Let's check local content
        letsencrypt = os.path.join(
                '/etc/letsencrypt',
                args.clouddomain
                )
        bot = certbot(conf, LOG)
        if os.path.exists(letsencrypt):
            # Let's Encrypt has already ran on the node
            # Let's try to renew
            if bot.renew():
                # We got a new certificate, install it and upload it
                tools.create_bundle(args.clouddomain, args.destination)
                client.push(os.path.join(letsencrypt, 'live', 'cert.pem'))
                client.push(os.path.join(letsencrypt, 'live', 'chain.pem'))
                client.push(
                        os.path.join(letsencrypt, 'live', 'privkey.pem')
                        )
                reload_haproxy = True
        else:
            # Register certbot, and query new certificate,
            # then push to secure backend
            bot.register()
            bot.create()
            tools.create_bundle(args.clouddomain, args.destination)
            client.push(os.path.join(letsencrypt, 'live', 'cert.pem'))
            client.push(os.path.join(letsencrypt, 'live', 'chain.pem'))
            client.push(
                    os.path.join(letsencrypt, 'live', 'privkey.pem')
                    )
            reload_haproxy = True
    else:
        # We're on a slave
        # Compare local bundle contain with remote one.
        local_cert = os.path.join(
                os.path.dirname(args.destination),
                'cert.pem'
                )
        local_chain = os.path.join(
                os.path.dirname(args.destination),
                'chain.pem'
                )
        local_key = os.path.join(
                os.path.dirname(args.destination),
                'key.pem'
                )
        if (not os.path.exists(local_cert) or
                not tools.compare_certs(
                    cert, open(local_cert, 'r').read())):
                    # replace local chain and re-bundle
                    with open(local_cert, 'w+') as f:
                        f.write(cert)
                    with open(local_chain, 'w+') as f:
                        f.write(chain)
                    with open(local_key, 'w+') as f:
                        f.write(key)
                    with open(args.destination, 'w+') as f:
                        f.write(cert)
                        f.write(chain)
                        f.write(key)
                    reload_haproxy = True
    if reload_haproxy:
        # Reload haproxy as we had some changes
        __haproxy = haproxy(LOG)
        __haproxy.reload()
