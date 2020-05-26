FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD [ "sh", "-c", "export FLASK_APP=index.py; echo $FLASK_APP; flask run --host=0.0.0.0"]