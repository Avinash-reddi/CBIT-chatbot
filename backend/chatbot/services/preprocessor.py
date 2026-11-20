from .intent_matcher import TextPreprocessor
from .text_corrector import normalize_input
from .synonym_map import get_canonical
from collections import Counter


def extract_keywords(text, top_n=5):
    corrected = normalize_input(text)
    tokens = TextPreprocessor.preprocess(corrected)
    freq = Counter(tokens)
    return [word for word, count in freq.most_common(top_n)]


def similarity_score(text_a, text_b):
    tokens_a = set(TextPreprocessor.preprocess(text_a))
    tokens_b = set(TextPreprocessor.preprocess(text_b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)
