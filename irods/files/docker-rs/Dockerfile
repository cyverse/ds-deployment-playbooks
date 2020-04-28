FROM cyverse/irods-rs:4.1.10

### Switch back to root for installation
USER root

### Stage NetCDF plugin RPMs
COPY irods-netcdf-build/packages/centos7/*.rpm /tmp/

### Install support for iRODS plugins
RUN yum --assumeyes install \
      https://files.renci.org/pub/irods/releases/4.1.10/centos7/irods-runtime-4.1.10-centos7-x86_64.rpm && \
### Install iRODS NetCDF plugins
    yum --assumeyes install \
      /tmp/irods-api-plugin-netcdf-1.0-centos7.rpm \
      /tmp/irods-icommands-netcdf-1.0-centos7.rpm \
      /tmp/irods-microservice-plugin-netcdf-1.0-centos7.rpm
### Install support for UUID generation
    yum --assumeyes install uuidd && \
### Install support for periphery script
    yum --assumeyes install moreutils && \
### Create Diffie-Hellman parameters
    yum --assumeyes openssl && \
    openssl genpkey -genparam \
        -algorithm DH -pkeyopt dh_paramgen_prime_len:4096 \
        -out /var/lib/irods/.irods/dhparams.pem \
      2>&1 && \
### Clean up installation artifacts
    yum --assumeyes clean all && \
    rm --force --recursive /var/cache/yum /tmp/* && \
### Create vault base
    mkdir /irods_vault

### Install Set AVU plugin
COPY --chown irods:irods \
  irods-setavu-plugin/libraries/centos7/libmsiSetAVU.so /var/lib/irods/plugins/microservices

### Install cmd scripts
COPY --chown irods:irods cmd/* /var/lib/irods/iRODS/server/bin/cmd/
RUN chmod ug+x /var/lib/irods/iRODS/server/bin/cmd/*

### Install iRODS configuration files
COPY --chown irods:irods etc/irods/* /etc/irods/
COPY --chown irods:irods var/lib/irods/.irods/* /var/lib/irods/.irods
RUN chmod --recursive ug+r /var/lib/irods && \
### Ensure /etc/irods/, .irods/, and log/ are group writeable
    chmod --recursive ug+rw /etc/irods/ /var/lib/irods/.irods /var/lib/irods/iRODS/server/log

### Add script to handle start and stop extras
COPY --chown irods:irods periphery.sh /periphery
RUN chmod ug+x /periphery

VOLUME /etc/irods/server-chain.crt
VOLUME /etc/irods/server.key
VOLUME /var/lib/irods/iRODS/server/log
VOLUME /var/lib/irods/iRODS/server/log/proc

EXPOSE 1247/tcp 1248/tcp 20000-20009/tcp 20000-20009/udp

ENV IRODS_CONTROL_PLANE_KEY=TEMPORARY__32byte_ctrl_plane_key
ENV IRODS_NEGOTIATION_KEY=TEMPORARY_32byte_negotiation_key
ENV IRODS_ZONE_KEY=TEMPORARY_zone_key

CMD [ "/periphery" ]

### Prepare onbuild instantiation logic
COPY on-build-instantiate.sh /on-build-instantiate
RUN chmod u+x /on-build-instantiate

ONBUILD ARG IRODS_CLERVER_USER=ipc_admin
ONBUILD ARG IRODS_DEFAULT_RES=CyVerseRes
ONBUILD ARG IRODS_HOST_UID
ONBUILD ARG IRODS_RES_SERVER
ONBUILD ARG IRODS_STORAGE_RES

ONBUILD RUN /on-build-instantiate && \
            rm --force /on-build-instantiate

ONBUILD VOLUME /irods_vault/"$IRODS_STORAGE_RES"

ONBUILD USER irods-host-user

ONBUILD ENV IRODS_STORAGE_RES="$IRODS_STORAGE_RES"
