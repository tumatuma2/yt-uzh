from functools import cache

from phrase_segmenter import Segmenter

@cache
def get_segmenter(lang: str):
    return Segmenter(lang)
