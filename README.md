# Introduction

Back end of free text search website based on Elasticsearch engine. This project developed a robust search web application that not only provides basic word search over the whole database capabilities but also incorporates features such as spelling correction, auto-completion, and synonym matching.

This work is the project under the master thesis at the University of Zurich and Allianz.

## Set up

First install Elasticsearch locally and record you own username and password. Default username is "elasticsearch", no need to change it.

Run the Elasticsearch service locally.

Clone the repository and add below configure files:

In directory /Script:

* elastic_config_local.json
```json
{
  "base_url": # The url of your local Elasticsearch service, The default is http://localhost:9200
  "user": # Your Elasticsearch username
  "password": # Your Elasticsearch password
 }
```

* oracle_config.json
```json
{
  "host": # Can be find in your Oracle configure file M:\oracle\network\admin\tnsnames.ora
  "service_name":# service name
  "schema": # schema name
  "user": # Your system name/Oracle username,
  "password": # Your IDSDS password
  "db_name": # datebase name
}
```

In directory： {where you installed Elasticsearchl}\elasticsearch-8.9.1\config\dictionaries 

* synonyms.txt
ipod, i-pod, i pod
foozball , foosball
universe , cosmos

In directory /sbx-search add file settings.ini or add variables in your environment variables

* environment variables
```
ELASTICSEARCH_URL
ELASTICSEARCH_PASSWORD
ELASTICSEARCH_USERNAME
```

* settings.ini
```
URL
USERNAME
PASSWORD
```

Run the following command to create an environment called sbx-elastic
```
conda create -n sbx-elastic python=3.10
```

Install required packages:
```
pip install -r requirements.txt
```

## Running APP

First run file /Scripts/create_elasticsearch_indices.py to create indexes

Then run file /Scripts/feed_index_suggester.py to feed data

Move to /api and run the below command to run the api:

```
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Deploying API

Before deploying a new elasticsearch instance, make sure that the CRD and the elastic operator are deployed.

https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-deploy-eck.html

```bash
az acr build --image sbx-elastic/search-api:develop --registry {register id} --file Dockerfile .

kubectl rollout restart deployment sbx-elastic -n sbx-elastic
```

## Feeding data to the Elasticsearch service in cloud

Get the Elasticsearch password in cloud
```
kubectl get secret elasticsearch-es-elastic-user --> base64 decode value (PASSWORD=$(kubectl get secret elasticsearch-es-elastic-user -n sbx-elastic -o go-template='{{.data.elastic | base64decode}}'))
```

Forward the local port 9200 to service elasticsearch-es-http
```
kubectl port-forward service/elasticsearch-es-http 9200 -n sbx-elastic
```

Run the Scripts to feed data.
