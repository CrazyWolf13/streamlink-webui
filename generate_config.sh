#!/bin/sh

cat <<EOF > /app/frontend/src/config.js
window.config = {
    baseURL: '${BASE_URL}'
};
EOF

exec "$@"