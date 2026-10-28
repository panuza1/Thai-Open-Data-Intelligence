from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).parent
SOURCE = 'https://github.com/open-admin-data/thailand-administrative-divisions'
REV = 'eef739a534e26181c86073d69e9aeb527110cf1a'
CATALOG = [
    {'id': 'provinces', 'title': 'จังหวัดในประเทศไทย | Thailand provinces', 'description': 'รายชื่อจังหวัด รหัส พิกัด จำนวนอำเภอและตำบลในแต่ละจังหวัด. Thai provinces, geographic coordinates, district and subdistrict counts.', 'path': 'data/provinces.json', 'source': f'{SOURCE}/blob/{REV}/data/all-province.json'},
    {'id': 'districts', 'title': 'อำเภอในประเทศไทย | Thailand districts', 'description': 'รายชื่ออำเภอ เขต จังหวัดต้นสังกัด พิกัด และจำนวนตำบล. Districts, parent province, coordinates and subdistrict counts.', 'path': 'data/districts.ndjson', 'source': f'{SOURCE}/blob/{REV}/data/all-district.json'},
]

def load_dataset(dataset_id: str) -> pd.DataFrame:
    item = next((x for x in CATALOG if x['id'] == dataset_id), None)
    if item is None:
        raise ValueError(f'Unknown dataset: {dataset_id}')
    path = ROOT / item['path']
    with path.open(encoding='utf-8') as f:
        rows = json.load(f) if path.suffix == '.json' else [json.loads(line) for line in f if line.strip()]
    return preprocess(rows)

def preprocess(rows: list[dict]) -> pd.DataFrame:
    result = []
    for row in rows:
        parent = row.get('parent') or {}
        counts = row.get('children_count') or {}
        geo = row.get('geo') or {}
        result.append({'id': str(row['id']), 'name_th': row['name']['local'], 'name_en': row['name']['en'],
                       'province_th': (parent.get('name') or {}).get('local'),
                       'districts': counts.get('district'), 'subdistricts': counts.get('subdistrict'),
                       'latitude': geo.get('lat'), 'longitude': geo.get('lon')})
    df = pd.DataFrame(result)
    for col in ['districts', 'subdistricts', 'latitude', 'longitude']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def insights(df: pd.DataFrame, column: str) -> list[str]:
    values = df.dropna(subset=[column])
    if values.empty:
        return []
    maximum = values.loc[values[column].idxmax()]
    return [f"{len(values):,} records have a value for {column}.",
            f"The median is {values[column].median():,.1f}; the mean is {values[column].mean():,.1f}.",
            f"The highest value is {maximum[column]:,.0f} in {maximum['name_th']} ({maximum['name_en']})."]
