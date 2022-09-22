FROM python:3.10
# Install Mozilla Firefox
RUN apt-get update && apt-get install -y firefox-esr
# Install Geckodriver for Firefox
ARG GECKO_DRIVER_VERSION="v0.31.0"
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/${GECKO_DRIVER_VERSION}/geckodriver-${GECKO_DRIVER_VERSION}-linux64.tar.gz\
    && tar -xvzf geckodriver-${GECKO_DRIVER_VERSION}-linux64.tar.gz\
    && rm geckodriver-${GECKO_DRIVER_VERSION}-linux64.tar.gz\
    && chmod +x geckodriver\
    && cp geckodriver /usr/local/bin/
# Copy script
WORKDIR /root
COPY requirements.txt /root
RUN pip install -r requirements.txt
COPY . /root
RUN chmod u+x run.sh
# Launch
# CMD ./run.sh
# CMD ls -al
CMD python -m fff