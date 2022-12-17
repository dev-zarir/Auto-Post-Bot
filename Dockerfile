FROM centos:7

WORKDIR /main

ADD ./main/* .

RUN yum install firefox -y

RUN yum install python3 -y

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]
