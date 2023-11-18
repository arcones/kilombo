import json
from unittest import TestCase

from kilombo.model.study_hierarchy import StudyHierarchy
from kilombo.service.external.ncbi.ncbi import NCBI


class NCBITest(TestCase):
    def test_get_study_gse_and_srp_if_present(self):
        with open("fixtures/ncbi_extractor/132_study_summaries.json") as file:
            study_summaries = json.load(file)
        study_hierarchy = StudyHierarchy(pending=study_summaries)
        NCBI(study_hierarchy).link_study_and_accessions()
        assert len(study_hierarchy.successful) == 60
        assert study_hierarchy.successful == {
            "200066763": {"gse": "GSE66763", "srp": "SRP056049"},
            "200077598": {"gse": "GSE77598", "srp": "SRP069333"},
            "200079014": {"gse": "GSE79014", "srp": "SRP071311"},
            "200084424": {"gse": "GSE84424", "srp": "SRP078531"},
            "200084699": {"gse": "GSE84699", "srp": "SRP079236"},
            "200091387": {"gse": "GSE91387", "srp": "SRP094853"},
            "200094730": {"gse": "GSE94730", "srp": "SRP099127"},
            "200104897": {"gse": "GSE104897", "srp": "SRP119856"},
            "200104898": {"gse": "GSE104898", "srp": "SRP119855"},
            "200110525": {"gse": "GSE110525", "srp": "SRP132774"},
            "200113973": {"gse": "GSE113973", "srp": "SRP144462"},
            "200114652": {"gse": "GSE114652", "srp": "SRP148460"},
            "200121703": {"gse": "GSE121703", "srp": "SRP166658"},
            "200122353": {"gse": "GSE122353", "srp": "SRP168313"},
            "200125581": {"gse": "GSE125581", "srp": "SRP181863"},
            "200127969": {"gse": "GSE127969", "srp": "SRP180896"},
            "200128615": {"gse": "GSE128615", "srp": "SRP188970"},
            "200129773": {"gse": "GSE129773", "srp": "SRP192495"},
            "200129774": {"gse": "GSE129774", "srp": "SRP192496"},
            "200130177": {"gse": "GSE130177", "srp": "SRP193448"},
            "200130975": {"gse": "GSE130975", "srp": "SRP197361"},
            "200133028": {"gse": "GSE133028", "srp": "SRP201915"},
            "200134895": {"gse": "GSE134895", "srp": "SRP216410"},
            "200138614": {"gse": "GSE138614", "srp": "SRP224883"},
            "200139006": {"gse": "GSE139006", "srp": "SRP226024"},
            "200141980": {"gse": "GSE141980", "srp": "SRP237508"},
            "200142085": {"gse": "GSE142085", "srp": "SRP237763"},
            "200143320": {"gse": "GSE143320", "srp": "SRP299727"},
            "200144496": {"gse": "GSE144496", "srp": "SRP245908"},
            "200144830": {"gse": "GSE144830", "srp": "SRP247484"},
            "200145044": {"gse": "GSE145044", "srp": "SRP247976"},
            "200146294": {"gse": "GSE146294", "srp": "SRP251583"},
            "200156742": {"gse": "GSE156742", "srp": "SRP278607"},
            "200156902": {"gse": "GSE156902", "srp": "SRP278818"},
            "200159035": {"gse": "GSE159035", "srp": "SRP286403"},
            "200161196": {"gse": "GSE161196", "srp": "SRP292009"},
            "200161654": {"gse": "GSE161654", "srp": "SRP292941"},
            "200163005": {"gse": "GSE163005", "srp": "SRP297575"},
            "200163338": {"gse": "GSE163338", "srp": "SRP298165"},
            "200166675": {"gse": "GSE166675", "srp": "SRP306114"},
            "200168288": {"gse": "GSE168288", "srp": "SRP309366"},
            "200168527": {"gse": "GSE168527", "srp": "SRP309931"},
            "200169189": {"gse": "GSE169189", "srp": "SRP311303"},
            "200169216": {"gse": "GSE169216", "srp": "SRP311342"},
            "200172475": {"gse": "GSE172475", "srp": "SRP315686"},
            "200172476": {"gse": "GSE172476", "srp": "SRP315687"},
            "200173182": {"gse": "GSE173182", "srp": "SRP316022"},
            "200173187": {"gse": "GSE173187", "srp": "SRP316025"},
            "200173789": {"gse": "GSE173789", "srp": "SRP318646"},
            "200174083": {"gse": "GSE174083", "srp": "SRP318929"},
            "200177046": {"gse": "GSE177046", "srp": "SRP323730"},
            "200178085": {"gse": "GSE178085", "srp": "SRP323918"},
            "200180755": {"gse": "GSE180755", "srp": "SRP329681"},
            "200180760": {"gse": "GSE180760", "srp": "SRP329687"},
            "200180761": {"gse": "GSE180761", "srp": "SRP329685"},
            "200181952": {"gse": "GSE181952", "srp": "SRP332229"},
            "200184098": {"gse": "GSE184098", "srp": "SRP337022"},
            "200186895": {"gse": "GSE186895", "srp": "SRP343946"},
            "200188320": {"gse": "GSE188320", "srp": "SRP344813"},
            "200190289": {"gse": "GSE190289", "srp": "SRP349436"},
        }
