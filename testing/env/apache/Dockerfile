FROM test-env-base:centos7

RUN yum install --assumeyes openssl

ARG DOMAIN=dstesting_default

COPY .tls/$DOMAIN.key /etc/pki/tls/private/
COPY .tls/$DOMAIN.crt .tls/ca.crt /etc/pki/tls/certs/
