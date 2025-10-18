FROM python:3.12-slim

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

VOLUME /app

ENV HOST=0.0.0.0
ENV PORT=80

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "python", "main.py" ]
