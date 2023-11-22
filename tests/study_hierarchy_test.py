from kilombo.model.failed_study import FailedStudy
from kilombo.model.failed_study_reason import FailedStudyReason
from kilombo.model.study_hierarchy import StudyHierarchy


def test_move_to_successful_and_reconcile():
    successful_study_id = '123456789'

    pending = {
        successful_study_id: {'GSE': 'GSE456789'},
    }

    study_hierarchy = StudyHierarchy(pending=pending)

    study_hierarchy.move_study_to_successful(successful_study_id, 'SRP123456')
    study_hierarchy.reconcile()

    assert not hasattr(study_hierarchy, 'pending')
    assert study_hierarchy.successful == {successful_study_id: {'gse': 'GSE456789', 'srp': 'SRP123456'}}
    assert study_hierarchy.count_total == 1
    assert study_hierarchy.count_successful == 1
    assert study_hierarchy.count_failed == 0


def test_move_to_failed_and_reconcile():
    failed_study_id = '987654321'

    pending = {
        failed_study_id: {'GSE': 'GSE654321'},
    }

    study_hierarchy = StudyHierarchy(pending=pending)

    study_hierarchy.move_study_to_failed(FailedStudy(failed_study_id, FailedStudyReason.PYSRADB_NONE_TYPE))
    study_hierarchy.reconcile()

    assert not hasattr(study_hierarchy, 'pending')
    assert study_hierarchy.failed == {failed_study_id: FailedStudyReason.PYSRADB_NONE_TYPE}
    assert study_hierarchy.count_total == 1
    assert study_hierarchy.count_successful == 0
    assert study_hierarchy.count_failed == 1


def test_move_all_around_and_reconcile():
    successful_study_ids = ['123456789', '234567891', '345678912']
    failed_study_ids = ['987654321', '876543219', '765432198']

    pending = {
        successful_study_ids[0]: {'GSE': 'GSE456789'},
        successful_study_ids[1]: {'GSE': 'GSE567891'},
        successful_study_ids[2]: {'GSE': 'GSE678912'},
        failed_study_ids[0]: {'GSE': 'GSE654321'},
        failed_study_ids[1]: {'GSE': 'GSE543219'},
        failed_study_ids[2]: {'GSE': 'GSE432198'},
    }

    study_hierarchy = StudyHierarchy(pending=pending)

    for successful_study_id in successful_study_ids:
        study_hierarchy.move_study_to_successful(successful_study_id, 'SRP123456')

    for failed_study_id in failed_study_ids:
        study_hierarchy.move_study_to_failed(FailedStudy(failed_study_id, FailedStudyReason.PYSRADB_NONE_TYPE))

    study_hierarchy.reconcile()

    assert not hasattr(study_hierarchy, 'pending')
    assert study_hierarchy.successful == {
        successful_study_ids[0]: {'gse': 'GSE456789', 'srp': 'SRP123456'},
        successful_study_ids[1]: {'gse': 'GSE567891', 'srp': 'SRP123456'},
        successful_study_ids[2]: {'gse': 'GSE678912', 'srp': 'SRP123456'},
    }

    assert study_hierarchy.failed == {
        failed_study_ids[0]: FailedStudyReason.PYSRADB_NONE_TYPE,
        failed_study_ids[1]: FailedStudyReason.PYSRADB_NONE_TYPE,
        failed_study_ids[2]: FailedStudyReason.PYSRADB_NONE_TYPE,
    }

    assert study_hierarchy.count_total == 6
    assert study_hierarchy.count_successful == 3
    assert study_hierarchy.count_failed == 3
