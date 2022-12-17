FROM centos:7

WORKDIR /main

ADD ./main/* .

RUN yum install firefox -y

RUN yum install python3 -y

RUN yum install postgresql -y

RUN yum install postgresql-devel -y

RUN yum install python-devel -y

RUN pip3 install --upgrade pip

RUN pip3 install setuptools-rust

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]
