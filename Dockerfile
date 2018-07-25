FROM python:slim
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
CMD python app.py