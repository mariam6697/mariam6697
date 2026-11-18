"""Replace low-signal activity rows with public GitHub profile counts."""
import argparse
import os
from pathlib import Path
from urllib.error import URLError
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from update_profile import fetch_json

PROFILE_API = "https://api.github.com/users/mariam6697"
XHTML = "http://www.w3.org/1999/xhtml"
SVG = "http://www.w3.org/2000/svg"
ROWS = {
    "pull requests reviewed": ("Public repositories", "M3 2h9v12H3z M5 2v12 M7 5h3"),
    "issues opened": ("Stars received", "M8 1l2 4.5 5 .5-3.7 3.3 1 4.7L8 11.5 3.7 14l1-4.7L1 6l5-.5z"),
    "issue comments": ("Followers", "M8 7a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M3 14v-1a5 5 0 0110 0v1z"),
}


def public_counts():
    profile = fetch_json(PROFILE_API)
    repositories = []
    for page in range(1, (profile["public_repos"] + 99) // 100 + 1):
        repositories.extend(fetch_json(f"{PROFILE_API}/repos?type=owner&per_page=100&page={page}"))
    owned = [repo for repo in repositories if not repo["fork"]]
    return len(owned), sum(repo["stargazers_count"] for repo in owned), profile["followers"]


def format_metrics(source, counts):
    document = minidom.parseString(source)
    matches = {}
    for field in document.getElementsByTagNameNS(XHTML, "div"):
        if field.getAttribute("class") != "field":
            continue
        for node in field.childNodes:
            if node.nodeType != node.TEXT_NODE:
                continue
            value = node.data.strip().lower().split(maxsplit=1)
            if len(value) == 2 and value[0].isdigit() and value[1] in ROWS:
                matches[value[1]] = (field, node)
    if set(matches) != ROWS.keys():
        raise ValueError("Expected activity rows missing from the metrics render")

    removed = 0
    for (key, (label, shape)), count in zip(ROWS.items(), counts):
        field, node = matches[key]
        if count <= 0:
            field.parentNode.removeChild(field)
            removed += 1
            continue
        icon = field.getElementsByTagNameNS(SVG, "svg")[0]
        for child in list(icon.childNodes):
            icon.removeChild(child)
        path = document.createElementNS(SVG, "path")
        path.setAttribute("d", shape)
        path.setAttribute("style", "fill:none;stroke:#959da5;stroke-width:1.3")
        icon.appendChild(path)
        node.data = f" {count} {label}"

    root = document.documentElement
    root.setAttribute("height", str(int(root.getAttribute("height")) - 19 * removed))
    return root.toxml() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    temporary = args.output.with_suffix(".tmp")
    try:
        formatted = format_metrics(args.source.read_text(encoding="utf-8"), public_counts())
        temporary.write_text(formatted, encoding="utf-8")
        os.replace(temporary, args.output)
    except (URLError, TimeoutError, ValueError, KeyError, TypeError, IndexError, ExpatError) as error:
        print(f"Metrics unavailable; keeping the previous render ({error}).")


if __name__ == "__main__":
    main()
