import logging
import time

from pysradb import SRAweb


def add_missing_srps(id_to_gse_and_srp_if_present: dict):
    response = {}

    init = time.time()
    missing_srps_count = 0

    for study_id, gse_and_srp_if_present in id_to_gse_and_srp_if_present.items():
        try:
            if "SRP" not in gse_and_srp_if_present:
                logging.info(f"Extracting from {gse_and_srp_if_present['GSE']} for study {study_id} the SRP...")
                srp_info = SRAweb().gse_to_srp(gse_and_srp_if_present["GSE"])
                missing_srps_count += 1
                response[study_id] = {"GSE": gse_and_srp_if_present["GSE"], "SRP": srp_info["study_accession"][0]}
                logging.info(f"Done extracting from {gse_and_srp_if_present['GSE']} for study {study_id} the SRP")
            else:
                response[study_id] = {"GSE": gse_and_srp_if_present["GSE"], "SRP": gse_and_srp_if_present["SRP"]}
        except Exception as exception:
            logging.error(f"PYSRADB response not expected for study id {study_id} and {gse_and_srp_if_present['GSE']}")
            logging.error(f"Exception {exception.__class__.__name__} with {exception.args}")

    end = time.time()

    logging.debug(f"Transformed details of {missing_srps_count} GSEs to SRPs in {round(end - init, 2)} seconds")

    return response
