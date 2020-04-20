#! /bin/bash
#
# Usage:
#  config.sh OS VERSION
#
# Parameter:
#  OS       The name of the operating system being configured.
#  VERSION  the major version of the OS to configure.
#
# This script configures the common ansible requirements
#


main()
{
  if [[ "$#" -lt 1 ]]
  then
    printf 'The OS name is required as the first argument\n' >&2
    return 1
  fi

  if [[ "$#" -lt 2 ]]
  then
    printf 'The OS version number is required as the second argument\n' >&2
    return 1
  fi

  local os="$1"
  local version="$2"

  # Install required packages
  if [[ "$os" = centos ]]
  then
    install_centos_packages "$version"
  else
    install_debian_packages "$version"

    # Allow root to login without a password
    sed --in-place 's/nullok_secure/nullok/' /etc/pam.d/common-auth
  fi

  # Remove root's password
  passwd -d root

  # Configure passwordless root ssh access
  ssh-keygen -q -f /etc/ssh/ssh_host_key -N '' -t rsa

  if ! [[ -e /etc/ssh/ssh_host_dsa_key ]]
  then
    ssh-keygen -q -f /etc/ssh/ssh_host_dsa_key -N '' -t dsa
  fi

  if ! [[ -e /etc/ssh/ssh_host_rsa_key ]]
  then
    ssh-keygen -q -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
  fi

  sed --in-place '/session    required     pam_loginuid.so/d' /etc/pam.d/sshd
  update_sshd_config
  mkdir --parents /var/run/sshd
  mkdir --mode 0700 /root/.ssh
}


install_centos_packages()
{
  local version="$1"

  rpm --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-"$version"
  yum --assumeyes install iptables-services libselinux-python openssh-server sudo
}


install_debian_packages()
{
  local version="$1"

  apt-get update -qq
  apt-get install -qq -y apt-utils 2> /dev/null

  apt-get install -qq -y \
    iptables jq openssh-server python-pip python-selinux python-virtualenv sudo
}


update_sshd_config()
{
  cat <<EOF | sed --in-place  --regexp-extended --file - /etc/ssh/sshd_config
s/#?PermitRootLogin .*/PermitRootLogin yes/
s/#?PermitEmptyPasswords no/PermitEmptyPasswords yes/
EOF
}


set -e

main "$@"
