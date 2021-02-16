#!/usr/bin/env python
import tqdm
from argparse import ArgumentParser
from urllib import request
from urllib.parse import urlencode
import os
import sys
from Bio.SeqIO import parse


def my_hook(t):
    """Wraps tqdm instance.
    https://github.com/tqdm/tqdm/blob/master/examples/tqdm_wget.py
    Don't forget to close() or __exit__()
    the tqdm instance once you're done with it (easiest using `with` syntax).
    -------
    """
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b
    return update_to


def download_taxa(taxa, locations, outdir, desc):
    """
    Accesses the BOLD API to download all sequences for a specific taxon

    :param taxa: Taxon to download
    :param locations: Geograpical location(s)
    :param outdir: Directory to store fasta file
    :param desc: Description for tqdm progress meter
    :return: counts of sequences and basepairs downloaded
    """
    api_base = "http://boldsystems.org/index.php/API_Public"
    endpoint = "sequence"
    countries = ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
                 "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia",
                 "Australia", "Austria", "Azerbaijan", "Bahamas", "Bangladesh",
                 "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan",
                 "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
                 "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso",
                 "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
                 "Caribbean Sea", "Cayman Islands", "Central African Republic",
                 "Chile", "China", "Colombia", "Comoros", "Cook Islands",
                 "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus",
                 "Czech Republic", "Democratic Republic of the Congo",
                 "Denmark", "Dominican Republic", "Ecuador", "Egypt",
                 "El Salvador", "Equatorial Guinea", "Estonia", "Ethiopia",
                 "Faeroe Islands", "Fiji", "Finland", "France", "French Guiana",
                 "French Polynesia", "Gabon", "Georgia", "Germany", "Ghana",
                 "Greece", "Greenland", "Guadeloupe", "Guatemala", "Guinea",
                 "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary",
                 "Iceland", "India", "Indian Ocean", "Indonesia", "Iran",
                 "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan",
                 "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo",
                 "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho",
                 "Liberia", "Libya", "Lithuania", "Luxembourg", "Macedonia",
                 "Madagascar", "Malawi", "Malaysia", "Malta",
                 "Marshall Islands", "Mauritius", "Mexico", "Micronesia",
                 "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
                 "Namibia", "Nepal", "Netherlands", "New Caledonia",
                 "New Zealand", "Nicaragua", "Niger", "Nigeria",
                 "North Atlantic Ocean", "North Korea",
                 "Northern Mariana Islands", "Norway", "Oman", "Pacific Ocean",
                 "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay",
                 "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico",
                 "Republic of the Congo", "Romania", "Russia", "Rwanda",
                 "Saint Helena Ascension and Tristan da Cunha",
                 "Saint Kitts and Nevis", "Saint Lucia",
                 "Saint Vincent and the Grenadines", "Sao Tome and Principe",
                 "Saudi Arabia", "Senegal", "Serbia", "Seychelles",
                 "Sierra Leone", "Slovakia", "Slovenia", "Solomon Islands",
                 "South Africa", "South Georgia and the South Sandwich Islands",
                 "South Korea", "Southern Ocean", "Spain", "Sri Lanka", "Sudan",
                 "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria",
                 "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste",
                 "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey",
                 "Turkmenistan", "Uganda", "Ukraine", "United Arab Emirates",
                 "United Kingdom", "United States",
                 "United States Virgin Islands", "Uruguay", "Uzbekistan",
                 "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia",
                 "Zimbabwe"]
    if locations is None:
        locations = countries
    tot_bp = tot_seqs = 0
    for country in locations:
        c = (country.replace(" ", "_")).replace("'", "")
        outfile = os.path.join(outdir, f"{taxa}-{c}.fasta")
        encoded_request = urlencode({"taxon": taxa, "geo": country})
        url = f"{api_base}/{endpoint}?{encoded_request}"
        print(url)
        with tqdm.tqdm(desc=desc, ncols=100, unit=" bytes") as t:
            reporthook = my_hook(t)
            # Download the fasta
            request.urlretrieve(url, outfile, reporthook=reporthook)
        # Generate statistics of sequences
        bp = 0
        seqs = 0
        with open(outfile, mode='r', encoding='windows-1252') as fh:
            for record in parse(fh, "fasta"):
                s = record.seq
                bp += s.count("A") + s.count("T") + s.count("G") + s.count("C")
                seqs += 1
                tot_bp += bp
                tot_seqs += 1
        sys.stderr.write(f"Wrote {seqs} seqs to {outfile}\n")
    return tot_seqs, tot_bp


def download_domains(arguments):
    """
    Wraps download of all taxa from one or more domains

    :param arguments: Arguments from main
    :return:
    """
    domain_dict = {
            "animals": ["Acanthocephala", "Acoelomorpha", "Annelida",
                        "Arthropoda", "Brachiopoda", "Bryozoa", "Chaetognatha",
                        "Chordata", "Cnidaria", "Ctenophora", "Cycliophora",
                        "Echinodermata", "Entoprocta", "Gastrotricha",
                        "Gnathostomulida", "Hemichordata", "Kinorhyncha",
                        "Mollusca", "Nematoda", "Nematomorpha", "Nemertea",
                        "Onychophora", "Phoronida", "Placozoa",
                        "Platyhelminthes", "Porifera", "Priapulida",
                        "Rhombozoa", "Rotifera", "Sipuncula", "Tardigrada",
                        "Xenacoelomorpha"],
            "plants": ["Bryophyta", "Chlorophyta", "Lycopodiophyta",
                       "Magnoliophyta", "Pinophyta", "Pteridophyta",
                       "Rhodophyta"],
            "fungi": ["Ascomycota", "Basidiomycota", "Chytridiomycota",
                      "Glomeromycota", "Myxomycota", "Zygomycota"],
            "protists": ["Chlorarachniophyta", "Ciliophora", "Heterokontophyta",
                         "Pyrrophycophyta"]}
    seqs = 0
    bp = 0
    if arguments.domains == "all":
        domains = ["animals", "plants", "fungi", "protists"]
    else:
        domains = arguments.domains
    for domain in domains:
        sys.stderr.write(f"-- Downloading domain {domain}\n")
        for tax in domain_dict[domain]:
            _seqs, _bp = download_taxa(tax, arguments.outdir, f"  -- {tax}: ")
            seqs += _seqs
            bp += _bp
    sys.stderr.write(f"{seqs} sequences downloaded, {bp} bp total\n")


def download_taxon(arguments):
    """
    Wraps download of one or more taxa

    :param arguments: Arguments from main
    :return:
    """
    seqs = 0
    bp = 0
    sys.stderr.write(f"-- Downloading taxa:\n")
    for tax in arguments.taxa:
        _seqs, _bp = download_taxa(tax, arguments.geo, arguments.outdir,
                                   f"  -- {tax}")
        seqs += _seqs
        bp += _bp
    sys.stderr.write(f"{seqs} sequences downloaded, {bp} bp total\n")


def main(arguments):
    os.makedirs(arguments.outdir, exist_ok=True)
    if arguments.domains:
        download_domains(arguments)
    else:
        download_taxon(arguments)


if __name__ == "__main__":
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--domains", nargs="+",
                       choices=["all", "animals", "plants",
                                "fungi", "protists"],
                       help="Specify domains to download sequences for.")
    group.add_argument("--taxa", nargs="+",
                       help="Specify one or more taxa")
    parser.add_argument("-o", "--outdir", default=".", help="Output directory")
    parser.add_argument("-g", "--geo", nargs="+", help="Geographical location")
    args = parser.parse_args()
    main(args)
