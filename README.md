# kilombo

Aggregation of [NCBI](https://www.ncbi.nlm.nih.gov/) searches.

Given a NCBI text query it gathers all related study IDs with the GSEs and SRPs.


## How to run it

Get installed [poetry](https://python-poetry.org/) and then:

```shell
    poetry install
    uvicorn kilombo.main:app
```

Server will listen in port 8000. You can check the functionality with this example query:

```shell
    curl --location 'localhost:8000/query-study-hierarchy?keyword=stroke%20AND%20single%20cell%20rna%20seq%20AND%20musculus'
```
