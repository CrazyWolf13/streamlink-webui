#!/bin/sh

cat <<EOF > /app/frontend/src/src/config.js
window.config = {
    baseURL: '${BASE_URL}'
};
EOF

exec "$@"