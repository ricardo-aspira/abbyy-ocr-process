FROM python:3.7.3

LABEL author="Ricardo Souza Morais"
LABEL author.email="ricardo.souza.morais@gmail.com"

RUN apt-get update

WORKDIR /usr/app

ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD ./* ./

ENTRYPOINT ["python", "process.py"]