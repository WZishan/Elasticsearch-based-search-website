from fastapi import FastAPI
from sbx_search import SearchWrapper, SearchResults
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://sbx-cockpit.aim-cluster-001.aim-general-d.gwc1.azure.aztec.cloud.allianz",
    "https://cockpit.aim-cluster-001.aim-general-d.gwc1.azure.aztec.cloud.allianz"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = SearchWrapper()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/investments")
async def search_investments(q: str, portfolio='S0871'):
    return await _search(q, _indexname('investments', portfolio))


@app.get("/cons_units")
async def search_cons_units(q: str, portfolio='S0871'):
    return await _search(q, _indexname('cons_units', portfolio))


@app.get("/mandates")
async def search_mandates(q: str, portfolio='S0871'):
    return await _search(q, _indexname('mandates', portfolio))


@app.get("/mandates")
async def search_ultimate_issuers(q: str, portfolio='S0871'):
    return await _search(q, _indexname('ultimate_issuers', portfolio))


@app.get("/carts")
async def search_carts(q: str, portfolio='S0871'):
    return await _search(q, _indexname('cart', portfolio))


@app.get("/countries")
async def search_countries(q: str, portfolio='S0871'):
    return await _search(q, _indexname('country_of_risk', portfolio))


@app.get("/many")
async def search_many(
    q: str,
    indices: list[str] = [
        'investments',
        'cons_units',
        'mandates',
        'ultimate_issuers',
        'cart',
        'country_of_risk'
    ],
    portfolio: str = 'S0871'
):
    index_names = [_indexname(index, portfolio) for index in indices]
    res = await client.search_async(
        q,
        index_names,
        boosting={
            _indexname('mandates', portfolio): 2.3,
            _indexname('cons_units', portfolio): 4.3,
            _indexname('ultimate_issuers', portfolio): 2.3,
            _indexname('cart', portfolio): 13.3,
            _indexname('country_of_risk', portfolio): 4.3
        },
        sort={
            '_score': 'desc',
            'value': 'desc'
        }
    )
    _normalize_indices(res)
    return res.to_dict()


def _normalize_indices(search_results: SearchResults):
    for res in search_results.contents:
        res.index = res.index.split('-')[-1]


def _indexname(index_type: str, portfolio: str):
    return f'{portfolio.lower()}-{index_type}'


async def _search(q: str, index: str):
    res = await client.search_async(q, index)
    return res.to_dict()

if __name__ == "__main__":
    # https://stackoverflow.com/questions/63177681/is-there-a-difference-between-running-fastapi-from-uvicorn-command-in-dockerfile
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
