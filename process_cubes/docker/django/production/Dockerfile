FROM javert899/pm4py:latest


COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN adduser --disabled-password --gecos '' django \
    && adduser django django

COPY ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

COPY . /app
RUN chown -R django /app

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]