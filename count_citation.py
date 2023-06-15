from __future__ import annotations
import requests
from rich import print
import pandas as pd
import plotly.express as px
from pathlib import Path


def load_dataframe_from_file(file_path: Path) -> pd.DataFrame:
    """
    Load DataFrame from file if it exists.
    """
    if file_path.exists():
        return pd.read_csv(file_path, sep="\t")
    return pd.DataFrame()


def query_api(papers: dict[str, str]) -> dict[str, list[str] | list[int]]:
    """
    Use requests to query pubmed API to get papers that cited each paper listed above.
    """
    df = {"papers": [], "nb_citations": []}
    http_headers = {"authorization": "YOUR-OPENCITATIONS-ACCESS-TOKEN"}

    for paper_ in papers:
        print(paper_)
        api_call = f"https://opencitations.net/index/coci/api/v1/references/{papers[paper_]}"
        r = requests.get(api_call, headers=http_headers)

        if r.status_code == 200:
            citing_papers = r.json()
            df["papers"].append(paper_)
            df["nb_citations"].append(len(citing_papers))

    return df


def save_dataframe_to_file(df: pd.DataFrame, file_path: Path):
    """
    Save DataFrame to TSV if output file does not exist.
    """
    if not df.empty and not file_path.exists():
        df.to_csv(file_path, sep="\t", index=False)


def plot_citation_count(df: pd.DataFrame):
    """
    Use Plotly to create a bar chart of the citation count.
    """
    fig = px.bar(df, x="papers", y="nb_citations", color="papers", title="foo")
    fig.show()


def main():
    # List dois for BIDS papers
    papers = {
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

    output_file = Path().cwd() / "count_citation.tsv"

    df = load_dataframe_from_file(output_file)

    if df.empty:
        df = query_api(papers)
        save_dataframe_to_file(df, output_file)

    plot_citation_count(df)


if __name__ == "__main__":
    main()
