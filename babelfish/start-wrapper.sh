#!/bin/sh
# Block TCP access to PostgreSQL 
# Yes, you could mess with listen_addresses and such in the entrypoint, but that doesn't work or it blocks both TDS and PostgreSQL
iptables -A INPUT -p tcp --dport 5432 -j REJECT
ip6tables -A INPUT -p tcp --dport 5432 -j REJECT

# Drop to postgres user and run original entrypoint
exec setpriv --inh-caps=-all --bounding-set=-all --reuid postgres --regid postgres --init-groups -- /start.sh "$@"