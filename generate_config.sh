#!/bin/sh

cat <<EOF > /app/frontend/src/public/config.js
window.config = {
    baseURL: '${BASE_URL}'
};
EOF

exec "$@"