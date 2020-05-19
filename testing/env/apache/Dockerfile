FROM test-env-base:centos7

RUN yum install --assumeyes openssl

ARG DOMAIN=dstesting_default

COPY .tls/private/$DOMAIN.key /etc/pki/tls/private/
COPY .tls/certs/$DOMAIN.crt .tls/certs/root.crt /etc/pki/tls/certs/
