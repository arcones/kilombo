import json
import logging

import aiohttp
import requests


class NCBIRequest:
    def __init__(self):
        self.NCBI_API_KEYS = ["ed06bd0f3c27a605d87e51e94eecab115908", "b81884ffa1519f17cae15f6bd21ac8070108"]
        self.NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.NCBI_ESEARCH_GDS_URL = f"{self.NCBI_EUTILS_BASE_URL}/esearch.fcgi?db=gds&retmode=json&&retmax=10000"
        self.NCBI_ESUMMARY_GDS_URL = f"{self.NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds&retmode=json"
        self.NCBI_RETRY_MAX = 100

    def fetch_study_list(self, keyword):
        url = f"{self.NCBI_ESEARCH_GDS_URL}&term={keyword}"
        logging.debug(f"HTTP GET started ==> {url}")
        response = requests.get(url)
        logging.debug(f"HTTP GET done ==> {url}")
        return response

    async def fetch_study_summaries(self, study_id: int):
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
