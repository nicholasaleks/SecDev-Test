#!/bin/sh
set -eux

main () {
  say 'Running the attack'
  docker-compose run attack
}

say () {
  set +x
  printf '\n\n%s\n' '--------------------------------------------------------------------------------'
  echo "$@"
  set -x
}

main "$@"
