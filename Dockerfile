FROM python:3
ADD . /weather-cli
WORKDIR /weather-cli
RUN pip install -r requirements.txt
CMD ["/bin/bash"]