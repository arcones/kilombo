__author__ = """Marta Arcones"""
__email__ = "marta.arcones@alumnos.upm.com"
__version__ = "0.0.1"

import logging

import aiohttp
import requests
from fastapi import FastAPI

from kilombo.service import kilombo

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


@app.get("/query-ncbi-gds")
async def query_ncbi_gds(keyword: str):
    return await kilombo.query_ncbi_gds(keyword)


@app.get("/prueba-aiohttp")
async def test():
    async with aiohttp.ClientSession() as session:
        NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        NCBI_ESUMMARY_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds"
        url = f"{NCBI_ESUMMARY_GDS_URL}&id=200207275&api_key=ed06bd0f3c27a605d87e51e94eecab115908"
        async with session.get(url) as resp:
            return await resp.text()


@app.get("/prueba-requests/")
async def test():
    async with aiohttp.ClientSession() as session:
        NCBI_EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        NCBI_ESUMMARY_GDS_URL = f"{NCBI_EUTILS_BASE_URL}/esummary.fcgi?db=gds"
        url = f"{NCBI_ESUMMARY_GDS_URL}&id=200207275&api_key=ed06bd0f3c27a605d87e51e94eecab115908"
        response = requests.get(url)
        return response.text
