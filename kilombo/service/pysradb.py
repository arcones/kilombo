import logging

from pysradb import SRAweb


def add_sra_study_accessions(id_to_gse_dict: dict):
    response = {}

    for study_id, geo_accession_id in id_to_gse_dict.items():
        try:
            logging.info(f"Extracting from geo accession id {geo_accession_id} for study {study_id} the SRP info...")
            srp_info = SRAweb().gse_to_srp(geo_accession_id)
            response[study_id] = {"geo_accession_id": geo_accession_id, "sra_study_accession": srp_info["study_accession"][0]}
            logging.info(f"Done extracting from geo accession id {geo_accession_id} for study {study_id} the SRP info")
        except Exception as exception:
            logging.error(f"PYSRADB response not expected for study id {study_id} and geo accession {geo_accession_id}")
            logging.error(f"Exception {exception.__class__.__name__} with {exception.args}")
    return response
