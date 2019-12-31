FROM ubuntu:disco

ENV LANG C.UTF-8

WORKDIR /opt/azafea/src

COPY Pipfile.lock .

ARG build_type
RUN apt --quiet --assume-yes update && \
    apt --quiet --assume-yes --no-install-recommends install \
        gcc \
        gir1.2-glib-2.0 \
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
        && \
    pip3 install pipenv && \
    pipenv install --ignore-pipfile && \
    if [ "${build_type}" = "dev" ]; then \
        # Install the development/test dependencies
        pipenv install --ignore-pipfile --dev \
    ; else \
        # Make some space for the production image
        apt --quiet --assume-yes autoremove --purge \
            gcc \
            libcairo2-dev \
            libffi-dev \
            libgirepository1.0-dev \
            libglib2.0-dev \
            libpq-dev \
            python3-dev \
            && \
        rm -rf /var/cache/{apt,debconf} /var/lib/apt/lists/* /var/log/{apt,dpkg.log} \
    ; fi

COPY . .

ENTRYPOINT ["pipenv", "run", "azafea"]
