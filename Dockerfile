FROM alpine:3.19

# Official Alpine repo - maintained by Alpine team
RUN apk add --no-cache \
    nmap \
    nmap-scripts \
    nmap-nselibs \
    python3 \
    py3-pip

RUN pip3 install flask gunicorn --break-system-packages

WORKDIR /app
COPY server.py .

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "server:app"]
