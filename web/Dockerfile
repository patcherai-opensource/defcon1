FROM python:3.12-slim@sha256:46cb7cc2877e60fbd5e21a9ae6115c30ace7a077b9f8772da879e4590c18c2e3

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        pkg-config \
        xz-utils \
        libjpeg-dev \
        libpng-dev \
        libwebp-dev \
        libgif-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://imagemagick.org/archive/releases/ImageMagick-7.1.2-23.tar.xz \
    -o /tmp/imagemagick.tar.xz
RUN mkdir -p /tmp/imagemagick
RUN tar -xJf /tmp/imagemagick.tar.xz \
    -C /tmp/imagemagick \
    --strip-components=1
RUN cd /tmp/imagemagick && \
    ./configure --prefix=/usr/local && \
    make -j"$(nproc)" && \
    make install && \
    ldconfig /usr/local/lib && \
    rm -rf /tmp/imagemagick /tmp/imagemagick.tar.xz


COPY bbbird_archive /app
COPY policy.xml /usr/local/etc/ImageMagick-7/policy.xml

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY run-web.sh /run-web.sh
RUN chmod +x /run-web.sh

ENV PYTHONUNBUFFERED=1


ENTRYPOINT ["/run-web.sh"]

