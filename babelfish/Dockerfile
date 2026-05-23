FROM jonathanpotts/babelfishpg:latest@sha256:3ffed225d984c55f19e2f1f836e9530ef8e8114fc7e853e2ddbf0a8d756a5342

USER root

RUN apt-get update && apt-get install -y --no-install-recommends iptables \
    && rm -rf /var/lib/apt/lists/*

COPY start-wrapper.sh /start-wrapper.sh
RUN chmod +x /start-wrapper.sh

ENTRYPOINT ["/start-wrapper.sh"]