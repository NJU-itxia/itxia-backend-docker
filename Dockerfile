FROM python:2.7

ENV PYTHONUNBUFFERED 1

ENV INSTALL_PATH /itxia
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
