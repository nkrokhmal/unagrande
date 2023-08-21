FROM python:3.10

ENV PYTHONPATH "${PYTHONPATH}:/utils/python-utils-ak"
RUN export PIP_DEFAULT_TIMEOUT=100

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN mkdir /utils
RUN pip install poetry && poetry config virtualenvs.create false && poetry install
ADD https://api.github.com/repos/akadaner/python-utils-ak/git/refs/heads/master version.json
RUN cd /utils && git clone https://github.com/akadaner/python-utils-ak.git && cd python-utils-ak && git pull

COPY . /app/
EXPOSE 5000