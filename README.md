# kilombo

Aggregation of [NCBI](https://www.ncbi.nlm.nih.gov/) searches.

## How to run it

Get installed [poetry](https://python-poetry.org/) and then:

```shell
    poetry install
    uvicorn kilombo.main:app
```

Server will listen in port 8000. You can check the functionality with this example query:

```shell
    curl --location 'localhost:8000/query-NCBI-gds?keyword=stroke%20AND%20single%20cell%20rna%20seq%20AND%20musculus'
```

## Known Issues
- NCBI queries returning more than 10000 results cannot be processed (`retstart` & `retmax` parameters iteration needed)
- Long times to download summaries, e.g, 202 summaries in 100 seconds (aprox. 0.5s per study summary)
