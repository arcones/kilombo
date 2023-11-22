import json
import logging

import aiohttp
import requests


class NCBIRequest:
    def __init__(self):
        self.NCBI_API_KEYS = ['ed06bd0f3c27a605d87e51e94eecab115908', 'b81884ffa1519f17cae15f6bd21ac8070108']
        self.NCBI_EUTILS_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        self.NCBI_ESEARCH_GDS_URL = f'{self.NCBI_EUTILS_BASE_URL}/esearch.fcgi?db=gds&retmode=json'
        self.NCBI_ESUMMARY_GDS_URL = f'{self.NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds&retmode=json'
        self.NCBI_RETRY_MAX = 10
        self.BATCH_SIZE = 500

    def esearch_study_list(self, keyword):
        url = f'{self.NCBI_ESEARCH_GDS_URL}&term={keyword}'
        logging.debug(f'HTTP GET started ==> {url}')
        response = self._paginated_esearch(url)
        logging.debug(f'HTTP GET done ==> {url}')
        return response

    def _paginated_esearch(self, url):
        retstart = 0
        paginated_url = url + f'&retmax={self.BATCH_SIZE}&usehistory=y'
        idlist = []
        while True:
            response = json.loads(requests.get(f'{paginated_url}&retstart={retstart}').text)
            idlist += response['esearchresult']['idlist']
            if int(response['esearchresult']['retmax']) < self.BATCH_SIZE:
                return idlist
            else:
                retstart += self.BATCH_SIZE

    async def esummary_study(self, study_id: int):
        logging.debug(f'Started get summary for study ==> {study_id}')
        unauthenticated_url = f'{self.NCBI_ESUMMARY_GDS_URL}&id={study_id}'
        retries_count = 1
        while retries_count < self.NCBI_RETRY_MAX:
            api_key = self.NCBI_API_KEYS[0] if retries_count % 2 == 0 else self.NCBI_API_KEYS[1]
            url = unauthenticated_url + f'&api_key={api_key}'
            async with aiohttp.ClientSession() as session:
                logging.debug(f'HTTP GET started ==> {url}')
                async with session.get(url) as response:
                    logging.debug(f'HTTP GET Done ==> {url}')
                    if response.status == 200:
                        logging.debug(f'Done get summary in retry #{retries_count} ==> {study_id}')
                        return json.loads(await response.text())
                    else:
                        retries_count += 1
                        logging.debug(f'Get a {response.status} from {url}, retries count incremented to {retries_count}')
        raise Exception(f'Unable to fetch {study_id} in {self.NCBI_RETRY_MAX} attempts')
