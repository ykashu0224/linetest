FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
RUN pip install --upgrade setuptools
RUN pip3 install social-auth-app-django
COPY . /code/