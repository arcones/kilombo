import asyncio
import json
import logging
import time

from kilombo.service.external.ncbi.ncbi_extractor import NCBIExtractor
from kilombo.service.external.ncbi.ncbi_request import NCBIRequest


class NCBI:
    def __init__(self, study_hierarchy):
        self.NCBI_STUDY_ID_MIN = 200000000
        self.NCBI_STUDY_ID_MAX = 299999999
        self.study_hierarchy = study_hierarchy
        self.ncbi_request = NCBIRequest()

    def get_study_list(self, search_keyword: str):
        logging.info(f"Get study list for keyword {search_keyword}...")
        ncbi_study_list_http_response = json.loads(self.ncbi_request.fetch_study_list(search_keyword).text)["esearchresult"]
        logging.info(f"Done get study list for keyword {search_keyword}")
        items = ncbi_study_list_http_response["idlist"]
        for item in items:
            if self._is_study(int(item)):
                self.study_hierarchy.add_pending_study(item)

    def _is_study(self, item: int) -> bool:
        return self.NCBI_STUDY_ID_MIN <= item <= self.NCBI_STUDY_ID_MAX

    async def get_study_summaries(self):
        init = time.perf_counter()

        for index, study_id in enumerate(self.study_hierarchy.pending):
            self.study_hierarchy.pending[study_id] = asyncio.create_task(self.ncbi_request.fetch_study_summaries(study_id))

        await asyncio.wait(self.study_hierarchy.pending.values())

        for study_id in self.study_hierarchy.pending:
            self.study_hierarchy.pending[study_id] = self.study_hierarchy.pending[study_id].result()["result"]

        end = time.perf_counter()

        logging.info(f"Fetched details of {len(self.study_hierarchy.pending)} studies in {round(end - init, 2)} seconds")

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
