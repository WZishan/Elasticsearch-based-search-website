FROM python:3.10

WORKDIR /code

COPY sbx-search sbx-search
COPY api api
COPY Scripts Scripts

WORKDIR /code/sbx-search

RUN pip install -r requirements.txt
RUN pip install .

WORKDIR /code

USER 1:1

EXPOSE 8000


ENTRYPOINT ["/bin/bash", "-c"]
CMD ["python api/main.py"]