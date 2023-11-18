import logging
import time

from kilombo.model.study_hierarchy import StudyHierarchy
from kilombo.service.external.ncbi.ncbi import NCBI
from kilombo.service.external.pysradb import add_missing_srps
from kilombo.service.external.pysradb import add_srrs


async def query_ncbi_gds(keyword):
    init = time.perf_counter()

    logging.info(f"Started the process for keyword ==>  {keyword}")
    study_hierarchy = StudyHierarchy()
    ncbi = NCBI(study_hierarchy)
    ncbi.get_study_list(keyword)
    await ncbi.get_study_summaries()
    ncbi.link_study_and_accessions()
    add_missing_srps(study_hierarchy)
    add_srrs(study_hierarchy)
    logging.info(f"Finished the process for input search ==>  {keyword}")

    end = time.perf_counter()

    logging.info(f"Fetched details of {study_hierarchy.count_total} studies in {round(end - init, 2)} seconds")

    return study_hierarchy
