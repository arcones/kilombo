import logging

from kilombo.service.ncbi import get_study_accession_list
from kilombo.service.ncbi import get_study_list
from kilombo.service.ncbi import get_study_summaries
from kilombo.service.pysradb import add_sra_study_accessions


async def query_ncbi_gds(keyword):
    logging.info("Started the query to gds database of NCBI...")
    study_ncbi_id_list = get_study_list(keyword)
    study_summaries = await get_study_summaries(study_ncbi_id_list)
    id_to_gse_dict = get_study_accession_list(study_summaries)
    id_to_gse_and_srp_dict = await add_sra_study_accessions(id_to_gse_dict)
    logging.info("Finished the query to gds database of NCBI")
    return id_to_gse_and_srp_dict
