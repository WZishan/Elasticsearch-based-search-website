from typing import Union
from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from .config import get, Config
from .config.search_attributes_mapping import get_default_attributes
import asyncio
import pandas as pd
from itertools import groupby

class SearchWrapper:

    def __init__(self):
        self.user = get(Config.USERNAME)
        self.password = get(Config.PASSWORD)
        self.url = get(Config.URL)

        self.client = AsyncElasticsearch(
            self.url,
            basic_auth=(
                self.user,
                self.password
            )
        )

    # not used currently
    def search(
        self,
        search_expr: str,
        index_name: str,
        boosting: dict = {},
        sort: dict = {},
        max_results: int = 30
    ) -> 'SearchResults':

        return asyncio.get_event_loop().run_until_complete(self.search_async(
            search_expr,
            index_name,
            boosting,
            sort,
            max_results
        ))
    async def search_async(
        self,
        search_expr: str,
        index: Union[str, list[str]],
        boosting: dict = {},
        sort: dict = {},
        max_results: int = 30
    ) -> 'SearchResults':
        if not isinstance(index, list):
            index = [index]
        query = QueryBuilder.free_text_search_expr(
            search_expr,
            sort,
            boosting
        )

        resp = await self.client.search(
            index=index,
            body=query,
            size=max_results
        )
        results = ResponseParser.parse(resp)
        return results


class QueryBuilder:

    @staticmethod
    def free_text_search_expr(
        search_str: str,
        sort: dict = {},
        boosting: dict = {}
    ):
        query_dict = {
            "query": {
                "multi_match": {
                    "query": search_str,
                    "type": "cross_fields",
                    "fields": ["title"],
                    "operator": "and"
                }
            },
            "sort": sort,
            "indices_boost": [{k : v} for k, v in boosting.items()],
            "suggest": {
                "text": search_str,
                "simple_phrase": {
                    "phrase": {
                        "field": "title.phrase",
                        "size": 5,
                        "max_errors": 2,
                        "direct_generator": [
                          {
                            "field": "title.phrase",
                            "min_doc_freq": 1
                          }
                        ],
                        "highlight": {
                          "pre_tag": "<em>",
                          "post_tag": "</em>"
                        }
                      }
                    },
                "simple_term": {
                    "term": {
                        "field": "title.term",
                        "sort": "frequency"
                        }
                    },
                "simple_completion": {
                    "prefix": search_str,
                    "completion": {
                        "field": "title.complete",
                        "size": 1000
                        }
                    }
                  }
                }
        return query_dict


class SearchContent:

    def __init__(self, score: float, id: str, index: str, values: dict[str, str]):
        self.score = score
        self.index = index
        self.values = values
        self.id = id

    def to_dict(self):
        return {
            'index': self.index,
            'score': self.score,
            'id': self.id,
            'values': self.values
        }

    def __repr__(self):
        return f'Score: {self.score}, Index: {self.index}, ID: {self.id}, Values: {self.values}'

    def __str__(self):
        return self.__repr__()

class SearchSuggestion:

    def __init__(self, score: float, value: str):
        self.score = score
        self.value = value


    def to_dict(self):
        return {
            'score': self.score,
            'value': self.value
        }

    def __repr__(self):
        return f'Score: {self.score}, Value: {self.value}'

    def __str__(self):
        return self.__repr__()

class SearchResults:

    def __init__(self, total_hits: float, contents: list[SearchContent], suggestions: list[SearchSuggestion]):
        self.total_hits = total_hits
        self.contents = contents
        self.suggestions = suggestions

    def to_dict(self):
        return {
            'total_hits': self.total_hits,
            'contents': [r.to_dict() for r in self.contents],
            'suggestions': [r.to_dict() for r in self.suggestions]
        }

    def sort(self, attr: str, descending=True):
        self.contents.sort(key=lambda item: (item.score, item.values[attr]), reverse=not descending)
        self.suggestions.sort(key=lambda item: item.score, reverse=not descending)

    def to_dataframe(self):
        return pd.DataFrame(
            [{'score': r.score, 'index': r.index, 'id': r.id, **r.values} for r in self.contents])

    def __repr__(self):
        return f'Total hits: {self.total_hits}, contents: {self.contents}, Suggestions: {self.suggestions}'


class ResponseParser:

    @staticmethod
    def filterSuggestion(resp: ObjectApiResponse) -> list[SearchSuggestion]:
        suggestion_lst = {}
        for key_type in resp['suggest']:
            suggest_with_type = resp['suggest'][key_type]
            if key_type == "simple_completion":
                # the default completion suggestions is sorted alphabetically, adjust it to sort base on frequency
                for suggests in suggest_with_type:
                    groupSuggestions = groupby(sorted(suggests["options"],key=lambda item: (item["text"].lower())),key=lambda item: (item["text"].lower()))
                    suggests["options"] = [{'text':k,"score":sum([score["_score"] for score in v])} for k,v in groupSuggestions]
                    suggests["options"].sort(key=lambda item: (item["score"]), reverse=True)
            #limit the number of each type of suggestions is up to 5
            for suggests in suggest_with_type:
                for d in suggests["options"][:min(len(suggests["options"]),5)]:
                    suggestion_lst[d['text'].lower()] = SearchSuggestion(
                        d["score"]+1, d['text'].lower()
                    )
        return list(suggestion_lst.values())

    @staticmethod
    def filterContent(resp: ObjectApiResponse) -> list[SearchContent]:
        # Remove "title" field, rearrange the value_type and value for front-end performance
        for d in resp['hits']['hits']:
            try:
                d['_source'][d['_source']['value_type']] = d['_source']['value']
            except:
                print("no value_type key")
            d['_source'].pop('title')
        content_lst = [SearchContent(
            d['_score'], d['_id'], d['_index'], d['_source']
        ) for d in resp['hits']['hits']]

        return content_lst
    @staticmethod
    def parse(resp: ObjectApiResponse) -> SearchResults:
        content_lst = ResponseParser.filterContent(resp)
        suggestion_lst = ResponseParser.filterSuggestion(resp)
        return SearchResults(resp['hits']['total']['value'], content_lst, suggestion_lst)
