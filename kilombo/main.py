__author__ = """Marta Arcones"""
__email__ = "marta.arcones@alumnos.upm.com"
__version__ = "0.0.1"

import logging

from fastapi import FastAPI

from kilombo.service import kilombo

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(filename)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


@app.get("/query-study-hierarchy")
async def query_study_hierarchy(keyword: str):
    return await kilombo.query_ncbi_gds(keyword)
