from kilombo.model.failed_study_reason import FailedStudyReason


class FailedStudy:
    def __init__(self, study_id, reason: FailedStudyReason):
        self.study_id = study_id
        self.reason = reason
