#!/bin/bash
echo '/home/agent' > ~/.last_dir
declare -p > ~/.last_env
exec "$@"