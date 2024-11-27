#!/bin/bash
echo '/' > ~/.last_dir
declare -p > ~/.last_env
exec "$@"