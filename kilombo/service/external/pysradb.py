import logging
import time

from pysradb import SRAweb

from kilombo.model.failed_study import FailedStudy
from kilombo.model.failed_study_reason import FailedStudyReason
from kilombo.model.study_hierarchy import StudyHierarchy


def add_missing_srps(study_hierarchy: StudyHierarchy):
    init = time.perf_counter()

    pending_items = study_hierarchy.pending.items()
    pending_items_length = len(pending_items)

    for study_id, gse_and_summary in pending_items:
        try:
            gse = gse_and_summary['GSE']
            srp = SRAweb().gse_to_srp(gse)['study_accession'][0]
            study_hierarchy.move_study_to_successful(study_id, srp)
            logging.debug(f'For {gse} the SRP is {srp}')
        except AttributeError as attribute_error:
            if attribute_error.name == 'rename':
                study_hierarchy.move_study_to_failed(FailedStudy(study_id, FailedStudyReason.PYSRADB_NONE_TYPE))
            else:
                raise Exception(f'Unknown attribute error with name {attribute_error.name}')
        except ValueError as value_error:
            if value_error.args[0] == 'All arrays must be of the same length':
                study_hierarchy.move_study_to_failed(FailedStudy(study_id, FailedStudyReason.PYSRADB_ARRAY_LENGTH))
            else:
                raise Exception(f'Unknown value error with {value_error.args[0]}')

    end = time.perf_counter()

    logging.info(f'Transformed details of {pending_items_length} GSEs to SRPs in {round(end - init, 2)} seconds')

    study_hierarchy.reconcile()


def add_srrs(study_hierarchy: StudyHierarchy):
    init = time.perf_counter()

    successful_items = study_hierarchy.successful.items()
    pending_items_length = len(successful_items)

    for study_id, identifiers in successful_items:
        try:
            srp = identifiers['srp']
            data_frame = SRAweb().srp_to_srr(srp)
            srrs = list(data_frame['run_accession'])
            study_hierarchy.add_srrs(study_id, srrs)
            logging.debug(f'For {srp} the SRRs are {srrs}')
        except AttributeError as attribute_error:
            if attribute_error.name == 'columns':
                logging.debug(f'For {srp}, it seems there are none SRRs')
            else:
                raise Exception(f'Unknown attribute error with name {attribute_error.name}')

    end = time.perf_counter()

    logging.info(f'Transformed details of {pending_items_length} SRPS to SRRs in {round(end - init, 2)} seconds')
