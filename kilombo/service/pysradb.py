import asyncio
import logging

from pysradb import SRAweb


async def add_sra_study_accessions(id_to_gse_dict: dict):
    responses = {}

    for study_id, geo_accession_id in id_to_gse_dict.items():
        try:
            logging.info(f"Extracting from geo accession id {geo_accession_id} for study {study_id} the SRP info...")
            srp_info = asyncio.create_task(_pysradb_gse_to_srp(geo_accession_id))
            responses[study_id] = srp_info, geo_accession_id
            logging.info(f"Done extracting from geo accession id {geo_accession_id} for study {study_id} the SRP info")
        except Exception as exception:
            logging.error(f"PYSRADB response not expected for study id {study_id} and geo accession {geo_accession_id}")
            logging.error(f"Exception {exception.__class__.__name__} with {exception.args}")

    all_tasks = asyncio.all_tasks()
    all_tasks_filtered = list(filter(lambda task: "_pysradb_gse_to_srp" in f"${task.get_coro().cr_code}", all_tasks))
    await asyncio.wait(all_tasks_filtered)

    for response in responses:
        try:
            result = responses[response][0].result()["study_accession"][0]
            responses[response] = {"geo_accession_id": responses[response][1], "sra_study_accession": result}
        except AttributeError:
            logging.error(f"Problemas con el {responses[response][1]} de donde no se puede sacar el SRP")
            responses[response] = {"geo_accession_id": responses[response][1], "sra_study_accession": "Unknown"}

    return responses


async def _pysradb_gse_to_srp(geo_accession_id: str):
    return SRAweb().gse_to_srp(geo_accession_id)
