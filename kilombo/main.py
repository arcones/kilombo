__author__ = """Marta Arcones"""
__email__ = "marta.arcones@alumnos.upm.com"
__version__ = "0.0.1"

import logging

from fastapi import FastAPI

from kilombo.service.ncbi import get_study_accession_list, get_study_list, get_study_summaries
from kilombo.service.pysradb import add_sra_study_accessions

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


@app.get("/query-NCBI-gds/")
async def read_item(keyword: str):
    logging.info("Started the query-NCBI-gds data retrieval operation...")
    study_ncbi_id_list = get_study_list(keyword)

    study_summaries = get_study_summaries(study_ncbi_id_list)

    id_to_gse_dict = get_study_accession_list(study_summaries)
    id_to_gse_and_srp_dict = add_sra_study_accessions(id_to_gse_dict)

    logging.info("Finish the query-NCBI-gds data retrieval operation...")
    return id_to_gse_and_srp_dict
