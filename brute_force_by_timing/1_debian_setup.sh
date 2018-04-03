#!/bin/sh

main () {
  set -eux

  say 'Add unstable archive to sources'
  echo 'deb http://deb.debian.org/debian unstable main' \
    | sudo tee --append /etc/apt/sources.list

  say 'Install'
  sudo sh <<EOF
    set -eux
    apt-get update
    apt-get install -y -t unstable docker.io
    apt-get install -y docker-compose
EOF

  say 'Start docker'
  sudo systemctl start docker

  say 'Add user to group'
  sudo usermod -a -G docker "$(id -un)"

  set +x
  cat - <<EOF
-------------------------------------------------------
Now you need to logout and log back into this system so
your user account can access docker.
-------------------------------------------------------
EOF
}

say () {
  set +x
  printf '\n\n%s\n' '--------------------------------------------------------------------------------'
  echo "$@"
  set -x
}

main "$@"
