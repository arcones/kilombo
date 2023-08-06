import requests, untangle

response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=multiple%20sclerosis%20AND%20rna%20seq")

obj = untangle.parse(response.content)

print(obj)
