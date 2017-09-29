# Certodia
Manage your ACME Let's Encrypt certificates and share them between your Controllers

## Purpose
This project intends to allow TripleO to provision a Let's Encrypt certificate for the
public Endpoints, and share it between your Controllers.

## Problematic
Let's Encrypt uses a bunch of validation, and none of them actually support a multi-server
setup.

### DNS validation
This validation has some limitation due to the DNS backend you can use for it. Not really 
a good solution in this case.

### Webroot validation
That one is the one we will use for Certodia. There are some difficulties we must overcome,
like the load-balancing between multiple backends.

## Prerequists
### Set HAProxy socket access level to admin
In order to do so, please set the following in your TripleO environment file:
```yaml
parameter_defaults:
  ControllerExtraConfig:
    tripleo::haproxy::haproxy_socket_access_level: 'admin'
```

and ensure it's deployed and applied correctly. In order to check that, you can run the
following command on your controllers:
```Bash
[root@controller-prod-0 ~]# grep socket /etc/haproxy/haproxy.cfg
  stats  socket /var/lib/haproxy/stats mode 600 level admin
```

### DNS record for the VIP
In order to use Let's Encrypt, you must have a fixed VIP for your public endpoint, and
associate your DNS record for the Cloud Domain to it.

### A running Custodia or FreeIPA Vault
#### Custodia
Please read more on the [project page](https://github.com/latchset/custodia). We advice you to
run the latest stable release directly from the sources in order to make it work.

A configuration example is provided in "examples" directory.

#### FreeIPA Vault
Lately, [FreeIPA](http://www.freeipa.org/page/Main_Page) has added a new service, Vault, based
on Custodia. Thus, if you have a FreeIPA running in your infrastructure, you can use it as a backend
in order to store the secrets you want to share.

## Container vs Baremetal
Starting Pike, TripleO pushes container-based services - certodia supports that, of course, and provides a Dockerfile in order
to build a container.

In order to ensure it's working, you'll need to share some volumes between containers, especially:

  - HAProxy socket (in admin) (rw by certodia)
  - HAProxy certificate directory (rw by certodia)
  - Horizon httpd root directory (rw by certodia)
  - Docker socket /var/run/docker.sock (rw by certodia)

For Baremetal (deprecated), nothing more than running the script with proper configuration is needed.

## Process
### Install certbot
We will install certbot directly from EPEL, activating that repository and configuring it
in order to allow only certbot and its dependencies to be installed from there. This
will prevent possible issues with packages versions.

### Check if we're on the "master" (does it have the VIP?)
Certodia will need to resolve the CloudDomain record in order to check if the associated IP is
attached to the current node. If so, it will consider it's running on the master.

### Check if there's already an x509 keypair for the CloudDomain
As Let's Encrypt paths are known, it will check if there are already a keypair present or not.

It will also check whether certbot has already been initialized (useful when the VIP moves to
another server after a certificate has already been issued).

#### No keypair
If nothing is present, it will do a request. In order to ensure the validation request will be
done on the current node, it will use HAproxy socket in order to deactivate all the other backends
in the "horizon" listener.

It will reactivate those backends once the validation is over.

#### Already present
If there's already a keypair, it will run the renew command of certbot.

### Check remote container (Vault or Custodia) content
It will then check the remote container, either in Custodia or in FreeIPA Vault.

#### Keypair already present
It will do some checksums tests in order to find out if the container is up-to-date or not. If there's
a checksum mismatch, the content will be replaced upstream.

#### Nothing there for now
It will push the private key, related certificate and chain to the remote container.

### No VIP attached to current node
This means we're not on the master, hence certbot has nothing to do - we will only rely on the remote
container content.

#### Check remote container (Vault or Custodia) content
It will check and fetch remote content - if there are nothing, for example while you deploy the stack
for the first time, it will wait until something shows up in the remote container.

#### Check local x509 information
If there are already local keypair, it will compare, and replace the local content by the remote.

### Reload HAproxy if needed
In any case, if there are local changes, it will reload HAproxy in order to activate the new certificates.
