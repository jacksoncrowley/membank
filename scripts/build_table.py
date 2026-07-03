"""Convert lipid_properties.csv into a static, browsable docs/index.html.

Run with: uv run scripts/build_table.py

Uses csv.DictReader (not manual splitting) because free-text columns like
`notes` contain embedded commas/quotes that break naive comma-splitting.
"""

import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "lipid_properties.csv"
OUT_PATH = ROOT / "docs" / "index.html"

HEADING_HTML = """
<h1>Lipid Membrane Properties Database</h1>
<p>
  A literature-curated database of lipid bilayer biophysical properties
  &mdash; area per lipid, bilayer thickness, acyl-chain order parameters, and
  a few mechanical moduli &mdash; from experiment and molecular-dynamics
  simulation. Each row below is one reported value from one source at one
  condition; the same property for the same lipid can appear many times with
  different values across labs, methods, and force fields &mdash; that
  disagreement is preserved intentionally, not averaged away. Every row links
  to its source DOI.
</p>
"""


def cell(value: str) -> str:
    """Render a CSV cell, treating empty/NA as blank rather than the string 'None'."""
    if value is None or value.strip().lower() in ("", "nan", "none"):
        return ""
    return html.escape(value)


def doi_cell(doi: str) -> str:
    doi = (doi or "").strip()
    if not doi:
        return ""
    escaped = html.escape(doi)
    return f'<a href="https://doi.org/{escaped}" target="_blank" rel="noopener">{escaped}</a>'


def build_rows(reader: csv.DictReader) -> tuple[list[str], list[str]]:
    fieldnames = reader.fieldnames or []
    rows_html = []
    for row in reader:
        cells = []
        for col in fieldnames:
            raw = row.get(col, "")
            cells.append(doi_cell(raw) if col == "source_doi" else cell(raw))
        rows_html.append("<tr><td>" + "</td><td>".join(cells) + "</td></tr>")
    return fieldnames, rows_html


def render(fieldnames: list[str], rows_html: list[str]) -> str:
    header_html = "".join(f"<th>{html.escape(col)}</th>" for col in fieldnames)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lipid Membrane Properties Database</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
{HEADING_HTML}
<input type="search" id="row-search" placeholder="Search all columns&hellip;" aria-label="Search table">
<p id="row-count"></p>
<table id="data-table">
<thead><tr>{header_html}</tr></thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table>
<script>
(function () {{
  var input = document.getElementById('row-search');
  var rows = document.querySelectorAll('#data-table tbody tr');
  var count = document.getElementById('row-count');
  function render() {{
    var q = input.value.toLowerCase();
    var shown = 0;
    rows.forEach(function (row) {{
      var match = row.textContent.toLowerCase().indexOf(q) !== -1;
      row.style.display = match ? '' : 'none';
      if (match) shown++;
    }});
    count.textContent = shown + ' / ' + rows.length + ' rows';
  }}
  input.addEventListener('input', render);
  render();
}})();
</script>
</body>
</html>
"""


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        fieldnames, rows_html = build_rows(csv.DictReader(f))
    OUT_PATH.write_text(render(fieldnames, rows_html), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(rows_html)} rows)")


if __name__ == "__main__":
    main()
