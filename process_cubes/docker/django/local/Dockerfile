FROM javert899/pm4py:latest


COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

WORKDIR /app

ENTRYPOINT ["/entrypoint"]