# Thai Open Data Intelligence

Explore Thai administrative geography with multilingual dataset search and transparent analytics.

- Search Thai and English with multilingual embeddings or a TF-IDF baseline.
- Filter province and district records, compare counts, and download CSV results.
- Read deterministic summaries and inspect the retrieval evaluation dashboard.
- Run the manually labeled search benchmark and automated tests locally.

**Stack:** Python, Streamlit, pandas, scikit-learn, Sentence Transformers, Plotly.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
python -m pytest -q
python evaluation.py
```

The model downloads on first semantic search; no API key is required.
On 8 Thai queries against 2 datasets, keyword Precision@1/MRR were 0.875/0.938;
semantic were 0.625/0.813. These author-labeled results are exploratory, not a
representative benchmark. See `data/evaluation.json` for latency and details.

**Data:** [Open Admin Data Thailand](https://github.com/open-admin-data/thailand-administrative-divisions),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Snapshot and limitations:
[DATA.md](DATA.md).
