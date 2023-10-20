FROM python:3.11
COPY ./src /src
COPY requirements.txt /src
WORKDIR /src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV ID=""
ENV PASSWORD=""
ENV FIELD1=""
ENV TIME1=""
ENV FIELD2=""
ENV TIME2=""
ENV LINETOKEN=""

ENTRYPOINT python main.py --id $ID --password $PASSWORD --field1 $FIELD1 --time1 $TIME1 --field2 $FIELD2 --time2 $TIME2 --linetoken $LINETOKEN
