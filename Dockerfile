FROM fedora:26

RUN dnf -y update
RUN dnf -y install git python2 python3 python3-tox

COPY . /app

WORKDIR /app

CMD tox -r
