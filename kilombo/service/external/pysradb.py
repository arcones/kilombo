import logging
import time

from pysradb import SRAweb

from kilombo.model.failed_study import FailedStudy
from kilombo.model.failed_study_reason import FailedStudyReason
from kilombo.model.study_hierarchy import StudyHierarchy


def add_missing_srps(study_hierarchy: StudyHierarchy):
    init = time.time()

    pending_items = study_hierarchy.pending.items()
    pending_items_length = len(pending_items)

    for study_id, gse_and_summary in pending_items:
        try:
            gse = gse_and_summary["GSE"]
            srp = SRAweb().gse_to_srp(gse)["study_accession"][0]
            study_hierarchy.move_study_to_successful(study_id, srp)
            logging.debug(f"For {gse} the SRP is {srp}")
        except AttributeError as attribute_error:
            if attribute_error.name == "rename":
                study_hierarchy.move_study_to_failed(FailedStudy(study_id, FailedStudyReason.PYSRADB_NONE_TYPE))
            else:
                raise Exception(f"Unknown attribute error with name {attribute_error.name}")
        except ValueError as value_error:
            if value_error.args[0] == "All arrays must be of the same length":
                study_hierarchy.move_study_to_failed(FailedStudy(study_id, FailedStudyReason.PYSRADB_ARRAY_LENGTH))
            else:
                raise Exception(f"Unknown value error with {value_error.args[0]}")

    end = time.time()

    logging.info(f"Transformed details of {pending_items_length} GSEs to SRPs in {round(end - init, 2)} seconds")

    study_hierarchy.reconcile()
