FROM centos:7

RUN yum update -y

ADD delorean.repo /etc/yum.repos.d/delorean-deps.repo
ADD tests/custodia/epel.repo /etc/yum.repos.d/epel.repo

RUN gpg --keyserver hkp://keys.gnupg.net --recv 91E97D7C4A5E96F17F3E888F6A2FAEA2352C64E5
RUN gpg --export --armor 91E97D7C4A5E96F17F3E888F6A2FAEA2352C64E5 > /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7


RUN yum install -y python-pip \
                    python2-pyOpenSSL \
                    python-netifaces \
                    python2-psutil \
                    python2-requests \
                    python2-cryptography \
                    PyYAML \
                    certbot \
                    git \
                    docker
RUN yum clean all
RUN git clone https://github.com/cjeanneret/openstack-certodia.git /opt/certodia
WORKDIR /opt/certodia/src
RUN make install
