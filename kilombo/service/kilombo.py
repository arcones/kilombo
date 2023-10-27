import logging

from kilombo.service.external.ncbi import get_study_gse_and_srp_if_present
from kilombo.service.external.ncbi import get_study_list
from kilombo.service.external.ncbi import get_study_summaries
from kilombo.service.external.pysradb import add_missing_srps


async def query_ncbi_gds(keyword):
    logging.info("Started the query to gds database of NCBI...")
    study_ncbi_id_list = get_study_list(keyword)
    study_summaries = await get_study_summaries(study_ncbi_id_list)
    id_to_gse_and_srp_if_present = get_study_gse_and_srp_if_present(study_summaries)
    id_to_gse_and_srp = add_missing_srps(id_to_gse_and_srp_if_present)
    logging.info("Finished the query to gds database of NCBI")
    return id_to_gse_and_srp
