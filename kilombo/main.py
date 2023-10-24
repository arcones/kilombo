__author__ = """Marta Arcones"""
__email__ = "marta.arcones@alumnos.upm.com"
__version__ = "0.0.1"

import logging

from fastapi import FastAPI

from kilombo.service import kilombo

app = FastAPI()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


@app.get("/query-ncbi-gds")
async def query_ncbi_gds(keyword: str):
    return await kilombo.query_ncbi_gds(keyword)
