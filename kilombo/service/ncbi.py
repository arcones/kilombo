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
        api_key = NCBI_API_KEYS[0] if index % 2 == 0 else NCBI_API_KEYS[1]
        responses[study_id] = asyncio.create_task(_fetch_study_summaries_aiohttp(study_id, api_key))

    all_tasks = asyncio.all_tasks()
    all_tasks_filtered = list(filter(lambda task: "_fetch_study_summaries_aiohttp" in f"${task.get_coro().cr_code}", all_tasks))
    await asyncio.wait(all_tasks_filtered)

    for response in responses:
        responses[response] = responses[response].result()

    end = time.time()

    logging.info(f"Fetched details of {len(study_id_list)} studies in {round(end - init, 2)} seconds")

    return responses


def get_study_accession_list(study_summaries: {}):
    responses = {}
    for study_summary in study_summaries:
        response = _extract_accessions_from_summaries(study_summaries[study_summary])
        if response.startswith("GSE"):
            responses[study_summary] = response
    return responses


def _extract_accessions_from_summaries(study_summary: dict):
    summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
    study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
    return study_accession["#text"]


def _extract_target_object_from_summaries(study_summary: dict):
    summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
    study_relations = next(filter(lambda item: item["@Name"] == "Relations", summary_payload))
    return study_relations["#text"]


def _fetch_study_list(keyword: str):
    url = f"{NCBI_ESEARCH_GDS_URL}&term={keyword}"
    logging.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    logging.debug(f"[HTTP] Done ==> {url}")
    return response


def _fetch_study_summaries(study_ncbi_id: int, api_key: str):
    url = f"{NCBI_ESUMMARY_GDS_URL}&id={study_ncbi_id}&api_key={api_key}"
    logging.debug(f"[HTTP] Started ==> {url}")
    response = requests.get(url)
    logging.debug(f"[HTTP] Done ==> {url}")
    return response


async def _fetch_study_summaries_aiohttp(study_ncbi_id: int, api_key: str):
    url = f"{NCBI_ESUMMARY_GDS_URL}&id={study_ncbi_id}&api_key={api_key}"
    while True:
        async with aiohttp.ClientSession() as session:
            logging.debug(f"[HTTP] Started ==> {url}")
            async with session.get(url) as response:
                logging.debug(f"[HTTP] Done ==> {url}")
                if response.status == 200:
                    logging.info(f"Done get summary for study {study_ncbi_id}")
                    return xmltodict.parse(await response.text())
                # else:
                #     logging.error(f"Call to NCBI responded with a {response.status}")
                #     raise Exception("NCBI response not expected... Shutting down")
