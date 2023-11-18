from kilombo.service.external.ncbi.ncbi_request import NCBIRequest


def test__paginated_esearch_no_iteration_needed(requests_mock):
    with open("fixtures/ncbi_request/retmax_7.json") as response:
        requests_mock.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json&retmax=500&usehistory=y&retstart=0", text=response.read())

    response = NCBIRequest()._paginated_esearch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json")

    assert response == ["200247102", "200207275", "200189432", "200167593", "200174574", "200126815", "200150644"]


def test__paginated_esearch_iteration_needed(requests_mock):
    with open("fixtures/ncbi_request/retmax_503_1.json") as response:
        requests_mock.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json&retmax=500&usehistory=y&retstart=0", text=response.read())

    with open("fixtures/ncbi_request/retmax_503_2.json") as response:
        requests_mock.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json&retmax=500&usehistory=y&retstart=500", text=response.read())

    response = NCBIRequest()._paginated_esearch("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&retmode=json")

    assert response == [str(x) for x in range(503)]
