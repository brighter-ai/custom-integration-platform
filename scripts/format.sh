#!/bin/bash

separator="==========================================================="
dunzo="Done! ✨"
space=" "
commands=(
"isort --profile=black -l=119,black --line-length 119,flake8 --exclude=*venv* --max-line-length=119"
)

if [ $1 ]; then
  argument=$@
else
  argument=$(git diff --name-only --cached)
fi

files=""
for item in $argument; do
  files+="${item} "
done


Backup_of_internal_field_separator=$IFS
IFS=,
for command in ${commands[@]}; do
  cmd="python3.10 -m ${command} ${files}"

  echo $separator
  echo $command
  echo $cmd
  echo $separator
  bash -c $cmd
  echo $dunzo
  echo $space
done

IFS=$Backup_of_internal_field_separator
