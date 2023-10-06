# kilombo

[![Build and test](https://github.com/arcones/kilombo/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/arcones/kilombo/actions/workflows/build-and-test.yml)

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
- Only checking GSE / GSM count of any study to call study details endpoint

## Ideas
- Hash study response and store to see if it has changed or not
- Using if needed several API keys to speed up parallel summaries downloads
