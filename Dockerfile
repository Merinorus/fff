FROM python:3.11-slim as base
ENV PYTHONUNBUFFERED=1
ARG GECKO_DRIVER_VERSION="v0.32.0"
ARG ARCH="linux64"

FROM base as buildstage

# Install Python libraries & Geckodriver
RUN apt-get update \
    && apt-get install -yq build-essential python3-dev wget \
    && apt-get clean \
    && pip3 install --upgrade pip \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q https://github.com/mozilla/geckodriver/releases/download/${GECKO_DRIVER_VERSION}/geckodriver-${GECKO_DRIVER_VERSION}-${ARCH}.tar.gz \
    && tar -xvzf geckodriver-${GECKO_DRIVER_VERSION}-linux64.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-${GECKO_DRIVER_VERSION}-${ARCH}.tar.gz

WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app
RUN pip3 install -r /usr/src/app/requirements.txt

FROM base as runtime-image

# Install Mozilla Firefox
RUN apt-get update \
    && apt-get upgrade -yq \
    && apt-get install -yq firefox-esr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies & Geckodriver
COPY --from=buildstage /usr/local/lib /usr/local/lib
COPY --from=buildstage /usr/local/bin /usr/local/bin

# Copy application
WORKDIR /usr/src/app
COPY . /usr/src/app
CMD python -m fff