from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np

try:
    from rank_bm25 import BM25Okapi

    BM25_OK = True
except Exception:  # pragma: no cover
    BM25_OK = False


_TOKEN_RE = re.compile(r"[\u0900-\u097Fa-zA-Z0-9]+")
_STOP = set("the a an is are was were be been being of to in on and or but if then else this that these those with by for from as at into about after over under it its not no do does did so such".split())


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    return [t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 1 and t.lower() not in _STOP]


@dataclass
class BM25Corpus:
    ids: list[int]
    texts: list[str]
    model: Optional["BM25Okapi"] = None

    def __len__(self) -> int:
        return len(self.ids)

    @classmethod
    def build(cls, sections: Iterable[object]) -> "BM25Corpus":
        ids: list[int] = []
        texts: list[str] = []
        tokenized: list[list[str]] = []
        for s in sections:
            joined = " ".join(
                x for x in [getattr(s, "title", ""), getattr(s, "section_number", ""), getattr(s, "bare_text", ""),
                           getattr(s, "plain_language", ""), " ".join(getattr(s, "keywords", []) or [])] if x
            )
            ids.append(int(getattr(s, "id", 0)))
            texts.append(joined)
            tokenized.append(_tokenize(joined))
        model = BM25Okapi(tokenized) if (BM25_OK and tokenized) else None
        return cls(ids=ids, texts=texts, model=model)

    def query(self, query: str, top_k: int = 50) -> list[tuple[int, float]]:
        tokens = _tokenize(query)
        if not tokens:
            return []
        if self.model is not None:
            scores = self.model.get_scores(tokens)
            if len(scores) == 0:
                return []
            top_idx = np.argsort(scores)[::-1][:top_k]
            out: list[tuple[int, float]] = []
            for idx in top_idx:
                sc = float(scores[idx])
                if sc <= 0:
                    continue
                out.append((self.ids[idx], sc))
            return out
        qset = set(tokens)
        scored: list[tuple[int, float]] = []
        for sid, text in zip(self.ids, self.texts):
            doc_tokens = _tokenize(text)
            if not doc_tokens:
                continue
            overlap = len(qset.intersection(doc_tokens))
            if overlap == 0:
                continue
            tf = sum(doc_tokens.count(t) for t in tokens)
            idf = np.log(1 + len(self.ids) / (1 + overlap))
            score = float(tf * idf)
            scored.append((sid, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
