#!/bin/bash

export ENV_NAME=dstesting
export DOMAIN="$ENV_NAME"_default

export DBMS_HOST="$ENV_NAME"_dbms_1."$DOMAIN"

export IRODS_IES_SYSTEM_GROUP=irods_ies
export IRODS_LAST_EPHEMERAL_PORT=20009
export IRODS_RS6_NAME=rs_centos6
export IRODS_RS7_NAME=rs_centos7
export IRODS_SCHEMA_VALIDATION=off
export IRODS_SSL_CA_CERTIFICATE_FILE=/etc/pki/tls/certs/irods-ca-bundle.pem
export IRODS_SSL_DH_PARAMS_FILE=/var/lib/irods/.irods/dhparams.pem
export IRODS_VAULT=/var/lib/irods/Vault
export IRODS_ZONE_NAME=testing

export IRODS_DEFAULT_RESOURCE="$IRODS_RS6_NAME"

export IRODS_IES_HOST="$ENV_NAME"_ies_1."$DOMAIN"
export IRODS_IES_UNCONF_HOST="$ENV_NAME"_ies_unconf_1."$DOMAIN"
export IRODS_IES_TLS_CERT_CHAIN=/etc/pki/tls/certs/server-chain.crt
export IRODS_IES_TLS_KEY=/etc/pki/tls/private/server.key

export IRODS_RS6_HOST="$ENV_NAME"_"$IRODS_RS6_NAME"_1."$DOMAIN"
export IRODS_RS7_HOST="$ENV_NAME"_"$IRODS_RS7_NAME"_1."$DOMAIN"
export IRODS_RS_TLS_CERT_CHAIN=/etc/pki/tls/certs/rs.crt
export IRODS_RS_TLS_KEY=/etc/pki/tls/private/rs.key
