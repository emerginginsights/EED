FROM python:3.8-slim-buster

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc && \
    apt-get clean

RUN apt-get install -y libpq-dev

COPY ./requirements /eed/requirements
COPY ./wbscript/requirements.txt /eed/wbscript/requirements.txt


RUN pip install --no-cache-dir -r /eed/requirements/prod.txt
RUN pip install --no-cache-dir -r /eed/wbscript/requirements.txt
RUN pip install gunicorn

COPY . /eed
WORKDIR /eed

EXPOSE 5000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000"]
