#!/usr/bin/env bash
set -o errexit
set -o xtrace



# parse arguments
while getopts "t:" opt; do
  case $opt in
    t) target="$OPTARG";;
    \?) echo "Invalid option -$OPTARG" >&2;;
  esac
done

# check if target is specified
if [ -z $target ]
  then echo "Please specify which docker target you want to run, e.g (-t production OR -t testing)."
  exit
fi

set -o nounset

pwd

name=$(awk '/^(name:|[0-9])/ { print $2}' ./build.info)
version=$(awk '/^(version:|[0-9])/ { print $2}' ./build.info)

docker build --target $target --no-cache --progress plain -f ./Dockerfile -t "${name}:${version}" ../
