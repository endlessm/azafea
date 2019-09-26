FROM ubuntu:disco

ENV LANG C.UTF-8

WORKDIR /opt/azafea/src

COPY Pipfile.lock .

RUN apt --quiet --assume-yes update \
    && apt --quiet --assume-yes --no-install-recommends install \
        gcc \
        gir1.2-glib-2.0 \
        git \
        gobject-introspection \
        libcairo2-dev \
        libffi-dev \
        libgirepository-1.0-1 \
        libgirepository1.0-dev \
        libglib2.0-dev \
        libpq5 \
        libpq-dev \
        python3 \
        python3-dev \
        python3-pip \
    && pip3 install pipenv \
    && pipenv install --ignore-pipfile \
    && apt --quiet --assume-yes autoremove --purge \
        gcc \
        libpq-dev \
        python3-dev \
    && rm -rf /var/cache/{apt,debconf} /var/lib/apt/lists/* /var/log/{apt,dpkg.log}

COPY . .

ENTRYPOINT ["pipenv", "run", "azafea"]
