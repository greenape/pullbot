FROM python:3-alpine
MAINTAINER Jonathan Gray <jonathan.gray@flowminder.org>
COPY assigner.py /assigner.py
COPY requirements.txt /requirements.txt
RUN pip install --pre -r requirements.txt
COPY token /gh_cred
COPY repos /repos
COPY user_rota /user_rota
EXPOSE 8080
CMD python /assigner.py