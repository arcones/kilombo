import logging


class NCBIExtractor:
    def __init__(self, study_id, study_hierarchy):
        self.study_id = study_id
        self.study_hierarchy = study_hierarchy

    def extract_gse_from_summaries(self):
        study_summary = self.study_hierarchy.pending[self.study_id]
        summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
        study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
        return study_accession["#text"] if study_accession["#text"].startswith("GSE") else None

    def extract_gsm_from_summaries(self):
        study_summary = self.study_hierarchy.pending[self.study_id]
        summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
        study_accession = next(filter(lambda item: item["@Name"] == "Accession", summary_payload))
        return study_accession["#text"] if study_accession["#text"].startswith("GSM") else None

    def extract_srp_from_summaries(self):
        try:
            study_summary = self.study_hierarchy.pending[self.study_id]
            summary_payload = study_summary["eSummaryResult"]["DocSum"]["Item"]
            study_relations = next(filter(lambda item: item["@Name"] == "ExtRelations", summary_payload))
            items = study_relations["Item"]["Item"]
            srp_if_present = [item for item in items if item["#text"].startswith("SRP")]
            return srp_if_present[0]["#text"] if len(srp_if_present) == 1 else None
        except KeyError:
            logging.debug(f"Missing SRP for study id {study_summary['eSummaryResult']['DocSum']['Id']}, setting it to None by the moment")
            return None
