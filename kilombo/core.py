import requests
import xmltodict

NCBI_E_UTILITIES_GDS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds"  # TODO ask claudivó if gds will be the db forever (there are more!)

EXAMPLE_QUERY = "multiple sclerosis AND rna seq"

main_query_response = requests.get(f"{NCBI_E_UTILITIES_GDS_BASE_URL}&term={EXAMPLE_QUERY}")

main_query_response_parsed = xmltodict.parse(main_query_response.text)

paper_ids = main_query_response_parsed["eSearchResult"]["IdList"]["Id"]

paper_response = requests.get(
    f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200239875&api_key=ed06bd0f3c27a605d87e51e94eecab115908"
)

paper_response_parsed = xmltodict.parse(paper_response.text)

print(paper_response_parsed)
