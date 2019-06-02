FROM python:3.7.3

LABEL author="Ricardo Souza Morais"
LABEL author.email="ricardo.souza.morais@gmail.com"

RUN apt-get update

RUN groupadd -r abbyocr && \
    useradd --no-log-init -r -g abbyocr abbyocr

WORKDIR /usr/app

RUN mkdir /usr/app/input && \
    mkdir /usr/app/output

ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD ./* ./

RUN chown abbyocr:abbyocr /usr/app -R

USER abbyocr

ENTRYPOINT ["python", "process.py"]