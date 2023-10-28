import asyncio
import logging
import time

import aiohttp
import requests
import xmltodict

from kilombo.model.failed_study import FailedStudy
from kilombo.model.failed_study_reason import FailedStudyReason
from kilombo.model.study_hierarchy import StudyHierarchy

NCBI_API_KEYS = ["ed06bd0f3c27a605d87e51e94eecab115908", "b81884ffa1519f17cae15f6bd21ac8070108"]

NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_ESEARCH_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esearch.fcgi?db=gds&retmax=10000"
NCBI_ESUMMARY_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds"

NCBI_RETRY_MAX = 100


def get_study_list(search_keyword: str, study_hierarchy: StudyHierarchy):
    logging.info(f"Get study list for keyword {search_keyword}...")
    ncbi_study_list_http_response = xmltodict.parse(_fetch_study_list(search_keyword).text)["eSearchResult"]
    logging.info(f"Done get study list for keyword {search_keyword}")
    study_ids = ncbi_study_list_http_response["IdList"]["Id"]
    for study_id in study_ids:
        study_hierarchy.add_pending_study(study_id)


async def get_study_summaries(study_hierarchy: StudyHierarchy):
    init = time.time()

    for index, study_id in enumerate(study_hierarchy.pending):
        study_hierarchy.pending[study_id] = asyncio.create_task(_fetch_study_summaries(study_id))

    await asyncio.wait(study_hierarchy.pending.values())

    for study_id in study_hierarchy.pending:
        study_hierarchy.pending[study_id] = study_hierarchy.pending[study_id].result()

    end = time.time()

    logging.info(f"Fetched details of {len(study_hierarchy.pending)} studies in {round(end - init, 2)} seconds")


def link_study_and_accessions(study_hierarchy: StudyHierarchy):
    for study_id in study_hierarchy.pending:
        gsm_if_found = _extract_gsm_from_summaries(study_hierarchy.pending[study_id])
        if gsm_if_found:
            logging.warning(f"For {study_id}, as GSM was found")
            study_hierarchy.move_study_to_failed(FailedStudy(study_id, FailedStudyReason.GSM_FOUND))
        else:
            gse_if_found = _extract_gse_from_summaries(study_hierarchy.pending[study_id])
            if gse_if_found:
                logging.info(f"For {study_id}, found GSE {gse_if_found}")
                study_hierarchy.pending[study_id]["GSE"] = gse_if_found
            srp_if_found = _extract_srp_from_summaries(study_hierarchy.pending[study_id])
            if srp_if_found:
                logging.info(f"For {study_id}, found SRP {srp_if_found}")
                study_hierarchy.move_study_to_successful(study_id, srp_if_found)
    study_hierarchy.reconcile()


def _extract_gse_from_summaries(study_summary: dict):
    summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
    study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
    return study_accession["#text"] if study_accession["#text"].startswith("GSE") else None


def _extract_gsm_from_summaries(study_summary: dict):
    summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
    study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
    return study_accession["#text"] if study_accession["#text"].startswith("GSM") else None


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
    logging.debug(f"HTTP GET started ==> {url}")
    response = requests.get(url)
    logging.debug(f"HTTP GET done ==> {url}")
    return response


async def _fetch_study_summaries(study_id: int):
    logging.debug(f"Started get summary for study ==> {study_id}")
    unauthenticated_url = f"{NCBI_ESUMMARY_GDS_URL}&id={study_id}"
    retries_count = 1
    while retries_count < NCBI_RETRY_MAX:
        api_key = NCBI_API_KEYS[0] if retries_count % 2 == 0 else NCBI_API_KEYS[1]
        url = unauthenticated_url + f"&api_key={api_key}"
        async with aiohttp.ClientSession() as session:
            logging.debug(f"HTTP GET started ==> {url}")
            async with session.get(url) as response:
                logging.debug(f"HTTP GET Done ==> {url}")
                if response.status == 200:
                    logging.debug(f"Done get summary in retry #{retries_count} ==> {study_id}")
                    return xmltodict.parse(await response.text())
                else:
                    retries_count += 1
                    logging.debug(f"Get a {response.status} from {url}, retries count incremented to {retries_count}")
    raise Exception(f"Unable to fetch {study_id} in {NCBI_RETRY_MAX} attempts")
