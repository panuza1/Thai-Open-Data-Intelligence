# Data provenance and limitations

Publisher: Open Admin Data, Thailand Administrative Divisions, CC BY 4.0:
https://github.com/open-admin-data/thailand-administrative-divisions
License: https://creativecommons.org/licenses/by/4.0/
Publisher update: 2026-06-01. Source revision: eef739a534e26181c86073d69e9aeb527110cf1a.
Accessed: 2026-10-28.

- `data/provinces.json`: unchanged `data/all-province.json` snapshot.
- `data/districts.ndjson`: transformed from `data/all-district.json` at that revision;
  one JSON object per line, preserving id, name, parent, children_count, geo and source.

The province fields include bilingual names, IDs, district and subdistrict counts and
coordinates. Districts include bilingual names, parent province, subdistrict counts
and coordinates. Numeric fields are coerced to numbers; missing values remain null.
The data is a single third-party snapshot, not a government census or a time series.
Counts are administrative units, not people. Coordinates and administrative boundaries
may change or contain errors; consult the publisher for current data. No trend is inferred.

The manually authored query set in `data/queries.json` uses binary relevance per dataset.
It is small, created alongside the catalog and has no independent annotator. Metrics
measure ranking in this two-item catalog only; MRR considers the full ranking and
Precision@1/Recall@1 use the first result. Warm latency excludes initialization and
model download, is measured once per query, and depends on hardware and load.
