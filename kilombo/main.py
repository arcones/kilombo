__author__ = """Marta Arcones"""
__email__ = "marta.arcones@alumnos.upm.com"
__version__ = "0.0.1"

from fastapi import FastAPI

from kilombo import ncbi_service

app = FastAPI()


@app.get("/query-NCBI-gds/")
async def read_item(keyword: str):
    study_ncbi_id_list = ncbi_service.get_study_list(keyword)

    return ncbi_service.get_study_summaries(study_ncbi_id_list)
