import logging

from kilombo.model.failed_study import FailedStudy
from kilombo.model.failed_study_reason import FailedStudyReason


class StudyHierarchy:
    def __init__(self, pending=None):
        if pending is None:
            pending = {}
        self.count_total = 0
        self.count_successful = 0
        self.count_failed = 0
        self.successful = {}
        self.pending = pending
        self.failed = {}

    def add_pending_study(self, study_id):
        self.pending[study_id] = {}

    def remove_study(self, study_id):
        del self.pending[study_id]

    def move_study_to_failed(self, failed_study: FailedStudy):
        self.failed[failed_study.study_id] = self.pending[failed_study.study_id]
        self.failed[failed_study.study_id] = failed_study.reason
        self.count_failed += 1
        assert len(self.failed) == self.count_failed
        self.count_total += 1
        assert len(self.successful) + len(self.failed) == self.count_total

    def move_study_to_successful(self, study_id, srp):
        self.successful[study_id] = {}
        self.successful[study_id]["gse"] = self.pending[study_id]["GSE"]
        self.successful[study_id]["srp"] = srp
        self.count_successful += 1
        assert len(self.successful) == self.count_successful
        self.count_total += 1
        assert len(self.successful) + len(self.failed) == self.count_total

    def add_srrs(self, study_id, srrs: []):
        self.successful[study_id]["srrs"] = srrs

    def reconcile(self):
        successful_study_ids_to_remove_from_pending = [study_id[0] for study_id in self.successful.items() if study_id[0] in self.pending.keys()]
        failed_study_ids_to_remove_from_pending = [study_id[0] for study_id in self.failed.items() if study_id[0] in self.pending.keys()]

        study_ids = successful_study_ids_to_remove_from_pending + failed_study_ids_to_remove_from_pending

        for study_id in study_ids:
            self.pending.pop(study_id)

        if len(self.pending) == 0:
            del self.pending
