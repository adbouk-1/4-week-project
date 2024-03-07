FROM python:3.11

WORKDIR /code

# RUN git clone https://github.com/adbouk-1/4-week-project.git

COPY ./src/ ./src/
COPY ./requirements.txt .

RUN apt-get -y -q update && \
  apt-get -y install \
  cmake g++ git python3 python3-pip python3-dev python3-venv \
  psmisc libfmt-dev libdrm-dev gcc make \
  libyaml-dev python3-yaml python3-ply python3-jinja2 \
  libssl-dev openssl meson libcap-dev 

# RUN  apt install -y libcamera-dev && \
#      apt full-upgrade -y

# COPY ./install_libcamera_all.sh .
# RUN ./install_libcamera_all.sh
# RUN pip install rpi-libcamera -C setup-args="-Drepository=https://github.com/raspberrypi/libcamera.git" -C setup-args="-Drevision=main"

# RUN apt-get -y install python3-picamera2
    
# RUN cd ./code/ 
# RUN python -m venv .
# ENV PATH="/opt/venv/bin:$PATH"

# RUN apt-get remove libcamera0
# RUN pip3 install jinja2 ply PyYAML

# COPY ./libcamera-0.2.0/ ./libcamera-0.2.0/ 

# RUN git clone https://github.com/raspberrypi/libcamera.git && \
    # cd libcamera && \
    # meson setup build && \
    # ninja -C build install

# RUN cd ./libcamera-0.2.0/ && \
#     meson setup build && \
#     ninja -C build install

# RUN pip install rpi-libcamera
RUN pip3 install -r ./requirements.txt
RUN pip3 install Office365-REST-Python-Client
RUN pip3 install pandas
# RUN python ./code/main.py

# RUN python main.py

CMD ["python",  "./src/main.py"]



