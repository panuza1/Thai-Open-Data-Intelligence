import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from data import CATALOG, SOURCE, load_dataset, insights
from search import KeywordSearch, SemanticSearch

st.set_page_config(page_title='Thai Open Data Intelligence', page_icon='◈', layout='wide')
st.markdown('''<style>
.block-container {max-width: 1200px; padding-top: 2.3rem;}
h1,h2,h3 {letter-spacing: -.035em;} [data-testid="stMetric"] {background:#151c31; border:1px solid #27314c; border-radius:14px; padding: 18px;}
[data-testid="stSidebar"] {border-right:1px solid #252e46;} a {color:#a7aaff;} .eyebrow {color:#a8aaff; font-size:.75rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase;}
</style>''', unsafe_allow_html=True)

@st.cache_data
def dataset(dataset_id):
    return load_dataset(dataset_id)

@st.cache_resource
def engine(method):
    return SemanticSearch() if method == 'Semantic' else KeywordSearch()

with st.sidebar:
    st.markdown('### ◈ &nbsp; THAI DATA')
    st.caption('OPEN DATA INTELLIGENCE')
    page = st.radio('Navigate', ['Overview', 'AI Search', 'Dataset Explorer', 'Model Evaluation'], label_visibility='collapsed')
    st.divider()
    st.caption('A small, attributed snapshot of Thailand’s administrative geography.')
    st.link_button('View source ↗', SOURCE)

st.markdown('<div class="eyebrow">Thai Open Data Intelligence / ' + page + '</div>', unsafe_allow_html=True)
if page == 'Overview':
    st.title('Explore Thailand, through data.')
    st.write('Discover and examine open administrative geography with multilingual search and transparent analysis.')
    provinces, districts = dataset('provinces'), dataset('districts')
    a, b, c = st.columns(3)
    a.metric('Provinces', f'{len(provinces):,}')
    b.metric('District records', f'{len(districts):,}')
    c.metric('Datasets', str(len(CATALOG)))
    st.subheader('Administrative divisions by province')
    st.caption('District counts reported in the province snapshot. Select Dataset Explorer for filters and records.')
    chart = provinces.nlargest(15, 'districts').sort_values('districts')
    st.plotly_chart(px.bar(chart, x='districts', y='name_th', orientation='h', color='districts', color_continuous_scale='Blues', labels={'districts':'Districts', 'name_th':'Province'}, template='plotly_dark'), width='stretch')
    st.info('Snapshot last updated by the publisher on 1 June 2026. Administrative counts are not population figures and the snapshot has no time series.')
elif page == 'AI Search':
    st.title('Find the right dataset.')
    st.write('Search descriptions in Thai or English. Results are ranked by similarity.')
    query = st.text_input('Search datasets', placeholder='เช่น รายชื่อจังหวัด หรือ district locations')
    method = st.radio('Retrieval method', ['Semantic', 'Keyword'], horizontal=True)
    if query.strip():
        try:
            with st.spinner('Preparing search… The model may download on first use.'):
                results = engine(method).search(query)
            if not results:
                st.info('No matching results. Try different keywords.')
            for item, score in results:
                with st.container(border=True):
                    st.subheader(item['title'])
                    st.write(item['description'])
                    st.caption(f'{method} cosine similarity: {score:.3f} · Scores are not probabilities')
                    st.link_button('Open original source ↗', item['source'])
            if method == 'Semantic':
                st.caption('Semantic search ranks the entire small catalog; a result can be irrelevant even if it appears here.')
        except Exception as exc:
            st.error(f'Search is unavailable: {exc}. Try keyword search or check the model download connection.')
    else:
        st.info('Enter a question to search the catalog.')
elif page == 'Dataset Explorer':
    st.title('Explore the data.')
    names = {x['title']:x for x in CATALOG}
    item = names[st.selectbox('Dataset', list(names))]
    st.write(item['description'])
    st.markdown(f"[Original source]({item['source']}) · CC BY 4.0 · Snapshot 2026-06-01")
    df = dataset(item['id'])
    if item['id'] == 'districts':
        options = sorted(df['province_th'].dropna().unique())
        selected = st.multiselect('Province', options)
        if selected:
            df = df[df['province_th'].isin(selected)]
    term = st.text_input('Filter names', placeholder='Thai or English')
    if term:
        df = df[df['name_th'].str.contains(term, case=False, regex=False, na=False) | df['name_en'].str.contains(term, case=False, regex=False, na=False)]
    st.metric('Matching records', f'{len(df):,}')
    if df.empty:
        st.info('No records match these filters.')
    else:
        column = 'districts' if item['id'] == 'provinces' else 'subdistricts'
        valid = df.dropna(subset=[column])
        if not valid.empty:
            st.subheader('What the data shows')
            for line in insights(df, column): st.write('• ' + line)
            chart = valid.nlargest(15, column).sort_values(column)
            st.plotly_chart(px.bar(chart, x=column, y='name_th', orientation='h', template='plotly_dark', color_discrete_sequence=['#8b8cff']), width='stretch')
        st.dataframe(df, width='stretch', hide_index=True)
        st.download_button('Download filtered CSV', df.to_csv(index=False).encode('utf-8-sig'), f"{item['id']}.csv", 'text/csv')
    st.caption('Counts and coordinates are supplied by the publisher. Missing values are excluded from summaries. Snapshot data cannot establish a trend.')
else:
    st.title('Retrieval, measured.')
    st.write('A small manually labeled Thai query set compares character n-gram TF-IDF with multilingual embeddings.')
    path = Path(__file__).parent/'data/evaluation.json'
    if not path.exists():
        st.warning('No benchmark has been generated. Run `python evaluation.py` to evaluate both models locally.')
    else:
        result = json.loads(path.read_text(encoding='utf-8'))
        rows = [{'Method': name.title(), 'Precision@1': result[name]['precision_at_1'], 'Recall@1': result[name]['recall_at_1'], 'MRR': result[name]['mrr'], 'Latency (ms)': result[name]['mean_latency_ms']} for name in ['keyword', 'semantic']]
        summary = pd.DataFrame(rows)
        st.dataframe(summary, hide_index=True, width='stretch')
        melted = summary.melt(id_vars='Method', value_vars=['Precision@1','Recall@1','MRR'], var_name='Metric', value_name='Score')
        st.plotly_chart(px.bar(melted, x='Metric', y='Score', color='Method', barmode='group', range_y=[0,1], template='plotly_dark', color_discrete_sequence=['#719fff','#ae8fff']), width='stretch')
        st.caption(f"{result['catalog_size']} datasets · {len(result['keyword']['queries'])} queries · warm per-query latency, excludes model initialization · {result['timestamp_utc']}")
        st.warning('This tiny, single-source catalog and author-labeled query set cannot establish general search quality. Scores and latency may vary by hardware.')
        with st.expander('Per-query results'):
            for name in ['keyword','semantic']:
                st.write(name.title())
                st.dataframe(pd.DataFrame(result[name]['queries']), hide_index=True)
