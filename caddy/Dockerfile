FROM caddy:2.9-builder AS builder

# Add module to proxy layer 4 (TCP) connections.
# Used to proxy postgres connections.
RUN xcaddy build \
    --with github.com/mholt/caddy-l4

FROM caddy:2.9

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
