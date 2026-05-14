ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python3 and pip (minimalmodbus/paho-mqtt/pyserial are pure Python)
RUN apk add --no-cache \
    python3 \
    py3-pip

# Copy isystem-to-mqtt source code
COPY isystem2mqtt/isystem-to-mqtt/ /isystem-to-mqtt/

WORKDIR /isystem-to-mqtt

# Install Python dependencies
RUN pip3 install --no-cache-dir minimalmodbus paho-mqtt && \
    pip3 install --no-cache-dir .

# Copy startup script
COPY isystem2mqtt/run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
