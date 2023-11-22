import logging


class NCBIExtractor:
    def __init__(self, study_id, study_hierarchy):
        self.study_id = study_id
        self.study_hierarchy = study_hierarchy

    def extract_gse_from_summaries(self) -> str:
        study_summary = self.study_hierarchy.pending[self.study_id]
        study_summary_payload = study_summary[study_summary['uids'][0]]
        if study_summary_payload['entrytype'] == 'GSE':
            return study_summary_payload['accession']

    def extract_srp_from_summaries(self) -> str:
        study_summary = self.study_hierarchy.pending[self.study_id]
        study_summary_payload = study_summary[study_summary['uids'][0]]
        if study_summary_payload['extrelations']:
            assert len(study_summary_payload['extrelations']) == 1
            sra_targetobject = study_summary_payload['extrelations'][0]['targetobject']
            if sra_targetobject.startswith('SRP'):
                return sra_targetobject
        else:
            logging.warning(f"Missing SRP for study id {study_summary['uids'][0]}, setting it to None by the moment")
