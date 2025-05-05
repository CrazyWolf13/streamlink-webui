#!/bin/sh

# Set the base URL for the frontend, from the env var to the config.js file
# This code ensures it runs inside docker but also inside a community-scripts-lxc
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

if [[ "$SCRIPT_PATH" == "/app/start.sh" ]]; then
  CONFIG_PATH="/app/frontend/src/dist/config.js"
else
  CONFIG_PATH="${SCRIPT_DIR%/*}/app/frontend/src/dist/config.js"
fi

cat <<EOF > "$CONFIG_PATH"
window.config = {
    baseURL: '${BASE_URL}'
};
EOF

# if env var Reverse_Proxy is set to true, then run fastapi with --proxy-headers
if [ "$REVERSE_PROXY" = True ]; then
    exec fastapi run main.py --proxy-headers
else
    exec fastapi run main.py
fi
