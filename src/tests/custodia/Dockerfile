FROM centos:latest
# install updates and custodia dependencies
RUN yum install -y epel-release
RUN yum -y update \
    && yum -y install \
        python-pip \
        python-requests python-six python-jwcrypto \
        python-ipaclient \
    && yum clean all

RUN pip install custodia

# Create Custodia user and group
# sum(ord(c) for c in 'cust') == 447
RUN groupadd -r custodia -g ${CUSTODIA_GID:-447} \
    && useradd -u ${CUSTODIA_GID:-447} -r -g custodia -d /var/lib/custodia -s /bin/bash -c "Custodia" custodia

# Directories
RUN install -d -m 755 -o custodia -g custodia \
    /etc/custodia \
    /var/log/custodia \
    /var/run/custodia \
    /var/lib/custodia

COPY custodia.conf /etc/custodia/
RUN chown custodia:custodia /etc/custodia/*.conf \
    && chmod 644 /etc/custodia/*.conf
CMD ["/usr/bin/custodia", "/etc/custodia/custodia.conf"]

USER custodia
