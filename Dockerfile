FROM ubuntu:disco

ENV LANG C.UTF-8

WORKDIR /opt/azafea/src

COPY Pipfile.lock .

RUN apt --quiet --assume-yes update \
    && apt --quiet --assume-yes --no-install-recommends install \
        gcc \
        git \
        libpq5 \
        libpq-dev \
        python3 \
        python3-dev \
        python3-pip \
    && pip3 install pipenv \
    && pipenv install --ignore-pipfile --dev \
    && apt --quiet --assume-yes autoremove --purge \
        gcc \
        git \
        libpq-dev \
        python3-dev \
    && rm -rf /var/cache/{apt,debconf} /var/lib/apt/lists/* /var/log/{apt,dpkg.log}

COPY . .

RUN pip3 install .

ENTRYPOINT ["pipenv", "run", "azafea"]
