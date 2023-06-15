from __future__ import annotations
import requests
from rich import print
import pandas as pd
import plotly.express as px
from pathlib import Path

# list dois for BIDS papers
papers: dict[str, str] = {
    "bids": "10.1038/sdata.2016.44",
    "bids-app": "10.1371/journal.pcbi.1005209",
    "EEG": "10.1038/s41597-019-0104-8",
    "iEEG": "10.1038/s41597-019-0105-7",
    "MEG": "10.1038/sdata.2018.110",
    "PET": "10.1038/s41597-022-01164-1",
    "Genetics": "10.1093/gigascience/giaa104",
    "Microscopy": "10.3389/fnins.2022.871228",
    "qMRI": "10.1038/s41597-022-01571-4",
    }


OUTPUT_FILE = Path().cwd() / "count_citation.tsv"

# load from file if it exists
if OUTPUT_FILE.exists():
    df = pd.read_csv(OUTPUT_FILE, sep="\t")

else:
    df: dict[str, list[str] | list[int]] = {"papers": [], "nb_citations": []}

    HTTP_HEADERS = {"authorization": "YOUR-OPENCITATIONS-ACCESS-TOKEN"}

    # use request to query pubmed API to get papers that cited each paper listed above
    for paper_ in papers:
        print(paper_)
        api_call = (
            f"https://opencitations.net/index/coci/api/v1/references/{papers[paper_]}"
        )
        r = requests.get(api_call)

        # if request fails print error and continue
        if r.status_code != 200:
            continue

        df["papers"].append( paper_)

        # if success get number of papers
        citing_papers = r.json()

        df["nb_citations"].append(len(citing_papers))

    df = pd.DataFrame(df)

    # save to tsv if output file does not exist
    if not df.empty and not OUTPUT_FILE.exists():
        df.to_csv(OUTPUT_FILE, sep="\t", index=False)

fig = px.bar(df, x="papers", y="nb_citations", color="papers", title="foo")
fig.show()