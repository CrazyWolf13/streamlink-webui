#!/bin/sh

# Set the base URL for the frontend, from the env var to the config.js file
cat <<EOF > /app/frontend/src/dist/config.js
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