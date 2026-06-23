# User Story 7: Data Mapping and Filtering

The script reads `raw_data.csv` and `reference_data.xlsx` with pandas, filters the
reference rows by `lookup_key`, removes duplicate lookup keys, and writes every
reference column to `output/mapped_output.csv`.

Install dependencies:

```bash
python3 -m pip install -r userStory7/requirements.txt
```

Run the program:

```bash
python3 -m userStory7.src.main
```

Run the tests:

```bash
python3 -m unittest userStory7.tests.test_mapper
```
