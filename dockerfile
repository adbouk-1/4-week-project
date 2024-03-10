FROM python:3.11

WORKDIR /code

COPY ./src/ ./src/
COPY ./requirements.txt .

RUN apt-get -y -q update && \
  apt-get -y install \
  cmake g++ git python3 python3-pip python3-dev python3-venv \
  psmisc libfmt-dev libdrm-dev gcc make \
  libyaml-dev python3-yaml python3-ply python3-jinja2 \
  libssl-dev openssl meson libcap-dev 

RUN pip3 install -r ./requirements.txt

CMD ["python",  "./src/main.py"]



