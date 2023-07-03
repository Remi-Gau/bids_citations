"""Guess gender of contributors to BIDS."""
from __future__ import annotations

from pathlib import Path

import gender_guesser.detector as gender
import ruamel.yaml


def root_dir():
    return Path(__file__).parent.resolve()


with open(root_dir() / "bids_spec_citation.cff") as f:
    cff = ruamel.yaml.load(f, Loader=ruamel.yaml.RoundTripLoader)

results = {
    "male": 0,
    "female": 0,
    "andy": 0,
    "unknown": 0,
    "mostly_male": 0,
    "mostly_female": 0,
}

d = gender.Detector()
for author in cff["authors"]:
    guess = d.get_gender(author["given-names"])
    print(f"{author['given-names']}: {guess}")
    results[guess] += 1

for key in results:
    print(f"- {key}: {results[key]}")
