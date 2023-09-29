# kilombo

[![Build and test](https://github.com/arcones/kilombo/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/arcones/kilombo/actions/workflows/build-and-test.yml)

Automate NIH search &amp; aggregation

## Known Issues
- NCBI queries returning more than 10000 results cannot be processed (`retstart` & `retmax` parameters iteration needed)
- Only checking GSE / GSM count of any study to call study details endpoint

## Ideas
- Hash study response and store to see if it has changed or not
- Using if needed several API keys to speed up parallel summaries downloads
