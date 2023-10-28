import logging
import time

from kilombo.model.study_hierarchy import StudyHierarchy
from kilombo.service.external.ncbi import get_study_list
from kilombo.service.external.ncbi import get_study_summaries
from kilombo.service.external.ncbi import link_study_and_accessions
from kilombo.service.external.pysradb import add_missing_srps


async def query_ncbi_gds(keyword):
    init = time.time()

    logging.info(f"Started the process for keyword ==>  {keyword}")
    study_hierarchy = StudyHierarchy()
    get_study_list(keyword, study_hierarchy)
    await get_study_summaries(study_hierarchy)
    link_study_and_accessions(study_hierarchy)
    add_missing_srps(study_hierarchy)
    logging.info(f"Finished the process for input search ==>  {keyword}")

    end = time.time()

    logging.info(f"Fetched details of {study_hierarchy.count_total} studies in {round(end - init, 2)} seconds")

    return study_hierarchy
