FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV INSTALL_PATH /src

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

ADD config/requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt