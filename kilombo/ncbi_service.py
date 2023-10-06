import concurrent.futures
import logging
import time

import requests
import xmltodict

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

NCBI_API_KEY = "ed06bd0f3c27a605d87e51e94eecab115908"

NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_ESEARCH_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esearch.fcgi?db=gds&retmax=10000"
NCBI_ESUMMARY_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds&api_key={NCBI_API_KEY}"


def get_study_list(search_keyword: str):
    ncbi_study_list_http_response = xmltodict.parse(_fetch_study_list(search_keyword).text)["eSearchResult"]
    return ncbi_study_list_http_response["IdList"]["Id"]


def get_study_summaries(study_id_list: []):
    responses = {}
    init = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for study_id, response in zip(study_id_list, executor.map(_fetch_study_items, study_id_list)):
            log.debug(f"Get summary for study {study_id}...")
            responses[study_id] = _retry_request_until_successful(_fetch_study_items, study_id)

    end = time.time()

    log.info(f"Fetched details of {len(study_id_list)} in {end - init} time")

    return responses


def _retry_request_until_successful(request, input):
    response = request(input)
    if response.status_code == 200:
        return xmltodict.parse(response.text)
    else:
        _retry_request_until_successful(request, input)


def _fetch_study_list(keyword: str):
    url = f"{NCBI_ESEARCH_GDS_URL}&term={keyword}"
    log.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    log.debug(f"[HTTP] Done ==> {url}")
    return response


def _fetch_study_items(study_ncbi_id: int):
    url = f"{NCBI_ESUMMARY_GDS_URL}&id={study_ncbi_id}"
    log.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    log.debug(f"[HTTP] Done ==> {url}")
    return response
