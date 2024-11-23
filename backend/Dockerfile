FROM python:3.12

ADD ./src /src
WORKDIR /src
EXPOSE 8000

RUN pip install -r requirements.txt

CMD ["fastapi", "run", "main.py"]