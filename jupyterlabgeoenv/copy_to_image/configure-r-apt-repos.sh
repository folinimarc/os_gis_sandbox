#!/bin/sh
set -eu

arch="$(dpkg --print-architecture)"
release="$(lsb_release -cs)"

wget -q -O- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc > /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
echo "deb [arch=${arch}] https://cloud.r-project.org/bin/linux/ubuntu ${release}-cran40/" > /etc/apt/sources.list.d/cran-r.list

case "${release}/${arch}" in
    noble/amd64|noble/arm64)
        wget -q -O- https://eddelbuettel.github.io/r2u/assets/dirk_eddelbuettel_key.asc > /etc/apt/trusted.gpg.d/cranapt_key.asc
        echo "deb [arch=${arch}] https://r2u.stat.illinois.edu/ubuntu ${release} main" > /etc/apt/sources.list.d/cranapt.list
        printf 'Package: *\nPin: release o=CRAN-Apt Project\nPin: release l=CRAN-Apt Packages\nPin-Priority: 700\n' > /etc/apt/preferences.d/99cranapt
        ;;
esac