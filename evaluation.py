import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from search import KeywordSearch, SemanticSearch, MODEL, REVISION
from data import CATALOG

ROOT = Path(__file__).parent

def metrics(ranked_ids, relevant, k=1):
    top = ranked_ids[:k]
    precision = sum(item in relevant for item in top) / k
    recall = len(set(top) & set(relevant)) / len(relevant) if relevant else 0.0
    rr = next((1 / (i + 1) for i, item in enumerate(ranked_ids) if item in relevant), 0.0)
    return precision, recall, rr

def evaluate(engine, labels):
    results = []
    engine.search('warm up')
    for item in labels:
        start = time.perf_counter()
        ranking = engine.search(item['query'])
        elapsed = (time.perf_counter() - start) * 1000
        p, r, rr = metrics([x['id'] for x, _ in ranking], set(item['relevant']))
        results.append({'query': item['query'], 'precision_at_1': p, 'recall_at_1': r, 'reciprocal_rank': rr, 'latency_ms': elapsed})
    return {'precision_at_1': sum(x['precision_at_1'] for x in results)/len(results),
            'recall_at_1': sum(x['recall_at_1'] for x in results)/len(results),
            'mrr': sum(x['reciprocal_rank'] for x in results)/len(results),
            'mean_latency_ms': sum(x['latency_ms'] for x in results)/len(results), 'queries': results}

def main():
    labels = json.loads((ROOT/'data/queries.json').read_text(encoding='utf-8'))
    known = {x['id'] for x in CATALOG}
    assert labels and all(x['relevant'] and set(x['relevant']) <= known for x in labels)
    output = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
              'model': MODEL, 'model_revision': REVISION, 'catalog_size': len(CATALOG),
              'keyword': evaluate(KeywordSearch(), labels), 'semantic': evaluate(SemanticSearch(), labels)}
    (ROOT/'data/evaluation.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
