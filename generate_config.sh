#!/bin/sh

cat <<EOF > /app/frontend/src/dist/config.js
window.config = {
    baseURL: '${BASE_URL}'
};
EOF

exec "$@"