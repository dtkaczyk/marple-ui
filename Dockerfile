FROM python:3.10-slim
RUN apt-get update; apt-get install -y curl unzip gcc python3-dev
WORKDIR /code
# set virtual env
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["streamlit", "run","app.py"]

