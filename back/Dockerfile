# syntax=docker/dockerfile:1
FROM ubuntu:22.04


RUN apt-get update && apt-get install -y python3 python3-pip

COPY . /

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "../eatAPI/manage", "runserver"]