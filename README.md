# Citation Count

This script queries the [OpenCitations](https://opencitations.net/index/coci) API to get the number of papers that cited a list of papers related to the [BIDS](https://bids.neuroimaging.io/) data organization standard. The resulting citation count is then visualized using [Plotly](https://plotly.com/python/).

## Requirements

- Python 3.6+
- `requests` library (for making HTTP requests)
- `pandas` library (for working with data)
- `plotly` library (for data visualization)
- `rich` library (for console output formatting)

To install the required packages, run the following command in your terminal:
```
pip install -r requirements.txt
```

## Usage

1. Clone the repository to your local machine.
2. Open the `count_citation.py` file and replace `YOUR-OPENCITATIONS-ACCESS-TOKEN` with your OpenCitations access token.
3. Run the script:
```
python count_citation.py
```
4. The citation count for each paper will be saved in a TSV file named `count_citation.tsv` in the same directory as the script.
5. A bar chart of the citation count will be displayed using your default browser.

## License

This code is licensed under the MIT License. See the `LICENSE` file for details.