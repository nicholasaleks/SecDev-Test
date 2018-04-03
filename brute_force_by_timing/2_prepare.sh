#!/bin/sh
set -eux

main () {
  say 'Build the docker image'
  docker-compose build

  say 'Compile the vulnerable program'
  docker-compose run attack make -B
}

say () {
  set +x
  printf '\n\n%s\n' '--------------------------------------------------------------------------------'
  echo "$@"
  set -x
}

main "$@"
