import asyncio
import json
import logging
import time

import aiohttp
import requests

from kilombo.service.external.ncbi.ncbiextractor import NCBIExtractor


class NCBI:
    def __init__(self, study_hierarchy):
        self.NCBI_API_KEYS = ["ed06bd0f3c27a605d87e51e94eecab115908", "b81884ffa1519f17cae15f6bd21ac8070108"]
        self.NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.NCBI_ESEARCH_GDS_URL = f"{self.NCBI_EUTILS_BASE_URL}/esearch.fcgi?db=gds&retmode=json&&retmax=10000"
        self.NCBI_ESUMMARY_GDS_URL = f"{self.NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds&retmode=json&"
        self.NCBI_RETRY_MAX = 100
        self.NCBI_STUDY_ID_MIN = 200000000
        self.NCBI_STUDY_ID_MAX = 299999999
        self.study_hierarchy = study_hierarchy

    def get_study_list(self, search_keyword: str):
        logging.info(f"Get study list for keyword {search_keyword}...")
        ncbi_study_list_http_response = json.loads(self._fetch_study_list(search_keyword).text)["esearchresult"]
        logging.info(f"Done get study list for keyword {search_keyword}")
        items = ncbi_study_list_http_response["idlist"]
        for item in items:
            if self._is_study(int(item)):
                self.study_hierarchy.add_pending_study(item)

    def _is_study(self, item: int) -> bool:
        return self.NCBI_STUDY_ID_MIN <= item <= self.NCBI_STUDY_ID_MAX

    def _fetch_study_list(self, keyword: str):
        url = f"{self.NCBI_ESEARCH_GDS_URL}&term={keyword}"
        logging.debug(f"HTTP GET started ==> {url}")
        response = requests.get(url)
        logging.debug(f"HTTP GET done ==> {url}")
        return response

    async def get_study_summaries(self):
        init = time.perf_counter()

        for index, study_id in enumerate(self.study_hierarchy.pending):
            self.study_hierarchy.pending[study_id] = asyncio.create_task(self._fetch_study_summaries(study_id))

        await asyncio.wait(self.study_hierarchy.pending.values())

        for study_id in self.study_hierarchy.pending:
            self.study_hierarchy.pending[study_id] = self.study_hierarchy.pending[study_id].result()["result"]

        end = time.perf_counter()

        logging.info(f"Fetched details of {len(self.study_hierarchy.pending)} studies in {round(end - init, 2)} seconds")

    async def _fetch_study_summaries(self, study_id: int):
        logging.debug(f"Started get summary for study ==> {study_id}")
        unauthenticated_url = f"{self.NCBI_ESUMMARY_GDS_URL}&id={study_id}"
        retries_count = 1
        while retries_count < self.NCBI_RETRY_MAX:
            api_key = self.NCBI_API_KEYS[0] if retries_count % 2 == 0 else self.NCBI_API_KEYS[1]
            url = unauthenticated_url + f"&api_key={api_key}"
            async with aiohttp.ClientSession() as session:
                logging.debug(f"HTTP GET started ==> {url}")
                async with session.get(url) as response:
                    logging.debug(f"HTTP GET Done ==> {url}")
                    if response.status == 200:
                        logging.debug(f"Done get summary in retry #{retries_count} ==> {study_id}")
                        return json.loads(await response.text())
                    else:
                        retries_count += 1
                        logging.debug(f"Get a {response.status} from {url}, retries count incremented to {retries_count}")
        raise Exception(f"Unable to fetch {study_id} in {self.NCBI_RETRY_MAX} attempts")

    def link_study_and_accessions(self):
        for study_id in self.study_hierarchy.pending:
            ncbi_extractor = NCBIExtractor(study_id, self.study_hierarchy)
            gse_if_found = ncbi_extractor.extract_gse_from_summaries()
            if gse_if_found:
                logging.info(f"For {study_id}, found GSE {gse_if_found}")
                self.study_hierarchy.pending[study_id]["GSE"] = gse_if_found
            srp_if_found = ncbi_extractor.extract_srp_from_summaries()
            if srp_if_found:
                logging.info(f"For {study_id}, found SRP {srp_if_found}")
                self.study_hierarchy.move_study_to_successful(study_id, srp_if_found)
        self.study_hierarchy.reconcile()
