import asyncio
import logging
import time

import pandas
from pysradb import SRAweb


async def add_sra_study_accessions(id_to_gse_dict: dict):
    tasks = {}
    responses = {}

    init = time.time()

    for study_id, geo_accession_id in id_to_gse_dict.items():
        logging.info(f"Extracting from geo accession id {geo_accession_id} for study {study_id} the SRP info...")
        srp_info = asyncio.create_task(_pysradb_gse_to_srp(geo_accession_id))
        tasks[study_id] = srp_info, geo_accession_id
        # logging.info(f"Done extracting from geo accession id {geo_accession_id} for study {study_id} the SRP info")

    all_tasks = asyncio.all_tasks()
    all_tasks_filtered = list(
        filter(lambda task: "_pysradb_gse_to_srp" in f"${task.get_coro().cr_code}", all_tasks)
    )  ## Las tengo en un array asiq quiza puedo esperar por ellas sin filtros
    await asyncio.wait(all_tasks_filtered)

    for task in tasks:
        try:
            result = tasks[task][0].result()["study_accession"][0]
            responses[task] = {"geo_accession_id": tasks[task][1], "sra_study_accession": result}
        except Exception as exception:
            logging.error(f"PYSRADB response not expected for study id {study_id} and geo accession {geo_accession_id}")
            logging.error(f"Exception {exception.__class__.__name__} with {exception.args}")

    end = time.time()

    logging.info(f"Done pysradb {round(end - init, 2)} seconds")

    return responses


async def _pysradb_gse_to_srp(geo_accession_id: str):
    logging.info(f"PROCESSING {geo_accession_id}")
    result = SRAweb().gse_to_srp(geo_accession_id)  # https://pythonexamples.org/pandas-check-if-dataframe-is-empty/
    if result.empty:
        logging.info(f"EL DATAFRAME {geo_accession_id} ESTA EMPTY")
        return None
    logging.info(f"DONE {geo_accession_id}")
    return result
