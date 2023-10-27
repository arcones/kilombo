import asyncio
import logging
import time

import aiohttp
import requests
import xmltodict

NCBI_API_KEYS = ["ed06bd0f3c27a605d87e51e94eecab115908", "b81884ffa1519f17cae15f6bd21ac8070108"]

NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_ESEARCH_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esearch.fcgi?db=gds&retmax=10000"
NCBI_ESUMMARY_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds"

NCBI_RETRY_MAX = 100


def get_study_list(search_keyword: str):
    logging.info(f"Get study list for keyword {search_keyword}...")
    ncbi_study_list_http_response = xmltodict.parse(_fetch_study_list(search_keyword).text)["eSearchResult"]
    logging.info(f"Done get study list for keyword {search_keyword}")
    return ncbi_study_list_http_response["IdList"]["Id"]


async def get_study_summaries(study_id_list: []):
    responses = {}

    init = time.time()

    for index, study_id in enumerate(study_id_list):
        logging.info(f"Get summary for study {study_id}...")
        responses[study_id] = asyncio.create_task(_fetch_study_summaries(study_id))

    await asyncio.wait(responses.values())

    for response in responses:
        responses[response] = responses[response].result()

    end = time.time()

    logging.debug(f"Fetched details of {len(study_id_list)} studies in {round(end - init, 2)} seconds")

    return responses


def get_study_gse_and_srp_if_present(study_summaries: {}):
    responses = {}
    for study_summary in study_summaries:
        responses[study_summary] = {}
        gse_if_found = _extract_gse_from_summaries(study_summaries[study_summary])
        if gse_if_found is not None:
            responses[study_summary]["GSE"] = gse_if_found
        srp_if_found = _extract_srp_from_summaries(study_summaries[study_summary])
        if srp_if_found is not None:
            responses[study_summary]["SRP"] = srp_if_found
        if responses[study_summary] == {}:
            responses.pop(study_summary)
    return responses


def _extract_gse_from_summaries(study_summary: dict):
    summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
    study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
    return study_accession["#text"] if study_accession["#text"].startswith("GSE") else None


def _extract_srp_from_summaries(study_summary: dict):
    try:
        summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
        study_relations = next(filter(lambda item: item["@Name"] == "ExtRelations", summary_payload))
        items = study_relations["Item"]["Item"]
        srp_if_present = [item for item in items if item["#text"].startswith("SRP")]
        return srp_if_present[0]["#text"] if len(srp_if_present) == 1 else None
    except KeyError:
        logging.debug(f"Missing SRP for study id {study_summary['eSummaryResult']['DocSum']['Id']}, setting it to None by the moment")
        return None


def _fetch_study_list(keyword: str):
    url = f"{NCBI_ESEARCH_GDS_URL}&term={keyword}"
    logging.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    logging.debug(f"[HTTP] Done ==> {url}")
    return response


async def _fetch_study_summaries(study_ncbi_id: int):
    unauthenticated_url = f"{NCBI_ESUMMARY_GDS_URL}&id={study_ncbi_id}"
    retries_count = 1
    while retries_count < NCBI_RETRY_MAX:
        api_key = NCBI_API_KEYS[0] if retries_count % 2 == 0 else NCBI_API_KEYS[1]
        url = unauthenticated_url + f"&api_key={api_key}"
        async with aiohttp.ClientSession() as session:
            logging.debug(f"[HTTP] Started ==> {url}")
            async with session.get(url) as response:
                logging.debug(f"[HTTP] Done ==> {url}")
                if response.status == 200:
                    logging.debug(f"Done get summary for study {study_ncbi_id} in retry {retries_count}")
                    return xmltodict.parse(await response.text())
                else:
                    retries_count += 1
                    logging.debug(f"Get a {response.status} from {url}, retries count incremented to {retries_count}")
    raise Exception(f"Unable to fetch {study_ncbi_id} in {NCBI_RETRY_MAX} attempts")
