#!/usr/bin/env bash
cd build

if [ $# -eq 1 ]
then
  npx serve -s -p $1
else
  npx serve -s
fi
