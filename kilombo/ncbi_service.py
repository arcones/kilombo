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

    for study_id in study_id_list:
        log.debug(f"Get summary for study {study_id}...")
        response = _fetch_study_summaries(study_id)
        if response.status_code == 200:
            responses[study_id] = xmltodict.parse(response.text)
        else:
            raise Exception("NCBI response not expected...")

    end = time.time()

    log.debug(f"Fetched details of {len(study_id_list)} studies in {round(end - init, 2)} seconds")

    return responses


def get_study_accession_list(study_summaries: {}):
    responses = {}
    for study_summary in study_summaries:
        responses[study_summary] = _extract_accessions_from_summaries(study_summaries[study_summary])
    return responses


def _extract_accessions_from_summaries(study_summary: dict):
    summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
    study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
    return study_accession["#text"]


def _fetch_study_list(keyword: str):
    url = f"{NCBI_ESEARCH_GDS_URL}&term={keyword}"
    log.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    log.debug(f"[HTTP] Done ==> {url}")
    return response


def _fetch_study_summaries(study_ncbi_id: int):
    url = f"{NCBI_ESUMMARY_GDS_URL}&id={study_ncbi_id}"
    log.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    log.debug(f"[HTTP] Done ==> {url}")
    return response
