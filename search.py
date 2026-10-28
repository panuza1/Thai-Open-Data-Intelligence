import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from data import CATALOG

MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
REVISION = 'e8f8c211226b894fcb81acc59f3b34ba3efd5f42'

def documents():
    return [x['title'] + ' ' + x['description'] for x in CATALOG]

class KeywordSearch:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(documents())

    def search(self, query: str):
        if not query.strip():
            return []
        scores = (self.matrix @ self.vectorizer.transform([query]).T).toarray().ravel()
        return [(CATALOG[i], float(scores[i])) for i in np.argsort(-scores, kind='stable') if scores[i] > 0]

class SemanticSearch:
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(MODEL, revision=REVISION, device='cpu')
        self.matrix = self.model.encode(documents(), normalize_embeddings=True, show_progress_bar=False)

    def search(self, query: str):
        if not query.strip():
            return []
        vector = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
        scores = self.matrix @ vector
        return [(CATALOG[i], float(scores[i])) for i in np.argsort(-scores, kind='stable')]
