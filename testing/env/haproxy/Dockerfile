FROM test-env-base:centos7

RUN yum install --assumeyes epel-release
RUN rpm --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
RUN yum install --assumeyes openssl python-pip rsyslog
RUN pip --disable-pip-version-check install pyOpenSSL

COPY haproxy/config/iptables /etc/sysconfig

ARG DOMAIN=dstesting_default

COPY .tls/private/$DOMAIN.pem /etc/pki/tls/private/
