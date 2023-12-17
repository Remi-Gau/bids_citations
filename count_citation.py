from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
from pyzotero import zotero
from rich import print

DEBUG = True


# requires token from https://opencitations.net/index/coci/api/v1/token
# saved in token.txt


def load_dataframe_from_file(file_path: Path) -> pd.DataFrame:
    """
    Load DataFrame from file if it exists.
    """
    if file_path.exists():
        return pd.read_csv(file_path, sep="\t")
    return pd.DataFrame()


def return_citation_count_per_year(citations_doi: str) -> dict[str, int]:
    if not citations_doi:
        return {}
    citation_count_per_year = {}
    citations_doi = citations_doi.replace("; ", "__")
    if metadata := query_for_metadata(citations_doi):
        for citation in metadata:
            year = citation["year"]
            if year in citation_count_per_year:
                citation_count_per_year[year] += 1
            else:
                citation_count_per_year[year] = 1
    else:
        citations_doi = citations_doi.split("__")
        print(f" querying papers one by one: {citations_doi}")
        for citation in citations_doi:
            print(f"  querying: {citation}")
            if metadata := query_for_metadata(citation):
                year = metadata[0]["year"]
                if year in citation_count_per_year:
                    citation_count_per_year[year] += 1
                else:
                    citation_count_per_year[year] = 1
    return citation_count_per_year


def query_for_metadata(doi: str) -> dict[str, str]:
    with open("token.txt") as f:
        token = f.read().strip()
    headers = {"authorization": token}
    api_call = f"https://opencitations.net/index/coci/api/v1/metadata/{doi}"
    r = requests.get(api_call, headers=headers)
    if r.status_code == 200:
        return r.json()
    print(f"[red]Error: {r.status_code}[/red]")
    return {}


def query_api(papers: dict[str, str]) -> dict[str, list[str] | list[int]]:
    """
    Use requests to query papers that cited each paper listed in dict.
    """
    df = {"papers": [], "years": [], "nb_citations": []}

    for paper_ in papers:
        print(f" {paper_}")
        if metadata := query_for_metadata(papers[paper_]):
            print(metadata)
            if citations := metadata[0]["citation"]:
                citation_count_per_year = return_citation_count_per_year(citations)
                print(f" {citation_count_per_year}")
                for year in citation_count_per_year:
                    df["papers"].append(paper_)
                    df["years"].append(int(year))
                    df["nb_citations"].append(citation_count_per_year[year])

    return pd.DataFrame(df)


def save_dataframe_to_file(df: pd.DataFrame, file_path: Path):
    """Save DataFrame to TSV if output file does not exist."""
    if not df.empty and not file_path.exists():
        df.to_csv(file_path, sep="\t", index=False)


def plot_citation_count(df: pd.DataFrame):
    """
    Use Plotly to create a bar chart of the citation count per year stacked by paper.
    """
    fig = px.bar(
        df,
        x="years",
        y="nb_citations",
        color="papers",
        title="Citation count per year",
        labels={"years": "Year", "nb_citations": "Number of citations"},
    )
    fig.show()


def main():
    # List dois for BIDS papers from zotero group
    zot = zotero.Zotero(library_id="5111637", library_type="group")
    items = zot.everything(zot.top())
    papers = {}
    for item in items:
        title = item["data"].get("shortTitle") or item["data"].get("title")
        papers[title] = item["data"]["DOI"]

    output_file = Path().cwd() / "count_citation.tsv"

    df = load_dataframe_from_file(output_file)

    if df.empty:
        df = query_api(papers)
        save_dataframe_to_file(df, output_file)

    plot_citation_count(df)


if __name__ == "__main__":
    main()
