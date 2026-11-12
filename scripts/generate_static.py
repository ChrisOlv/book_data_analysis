from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT_DIR / "1.data" / "2.processed"
RAW_PAPER_DIR = ROOT_DIR / "1.data" / "1.raw" / "paper_audio"
OUTPUT_PATH = ROOT_DIR / "output" / "booklist.html"


def pick_existing_path(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Aucun fichier trouvé parmi : " + ", ".join(str(path) for path in candidates)
    )


def format_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.strftime("%Y-%m-%d").fillna("")


def safe_string(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def column_or_default(frame: pd.DataFrame, column_name: str, default: object = "") -> pd.Series:
  if column_name in frame.columns:
    return frame[column_name]
  return pd.Series(default, index=frame.index)


def load_ebook_books() -> pd.DataFrame:
    source = pick_existing_path(
        PROCESSED_DIR / "df_book_updated.parquet",
        PROCESSED_DIR / "df_book_updated_demo.parquet",
    )
    books = pd.read_parquet(source).copy()

    authors_column = "Auteurs courts" if "Auteurs courts" in books.columns else "Auteurs"
    progress = pd.to_numeric(column_or_default(books, "% lu"), errors="coerce")

    table = pd.DataFrame(
        {
        "Titre": safe_string(column_or_default(books, "Titre")),
        "Auteurs": safe_string(column_or_default(books, authors_column)),
        "Catégorie": safe_string(column_or_default(books, "Catégorie")),
            "Statut": progress.ge(90).map({True: "Fini", False: "En cours"}).fillna("En cours"),
        "Pages": pd.to_numeric(column_or_default(books, "# pages"), errors="coerce"),
        "Date de lecture": format_date(column_or_default(books, "Date de lecture")),
        }
    )

    return table


def load_paper_audio_books() -> pd.DataFrame:
    source = pick_existing_path(
        RAW_PAPER_DIR / "paper_audio.xlsx",
        RAW_PAPER_DIR / "paper_audio_demo.xlsx",
    )
    books = pd.read_excel(source).copy()

    pages_column = "# pages lues" if "# pages lues" in books.columns else None

    table = pd.DataFrame(
        {
        "Titre": safe_string(column_or_default(books, "Titre")),
        "Auteurs": safe_string(column_or_default(books, "Auteurs")),
            "Catégorie": "",
            "Statut": "Fini",
        "Pages": pd.to_numeric(column_or_default(books, pages_column), errors="coerce") if pages_column else pd.NA,
        "Date de lecture": format_date(column_or_default(books, "date de lecture")),
        }
    )

    return table


def build_catalog() -> pd.DataFrame:
    catalog = pd.concat([load_ebook_books(), load_paper_audio_books()], ignore_index=True)
    catalog = catalog[(catalog["Titre"] != "") & (catalog["Titre"] != "ERROR: Error reading EPUB format")]
    catalog["sort_date"] = pd.to_datetime(catalog["Date de lecture"], errors="coerce")
    catalog = catalog.sort_values(by=["sort_date", "Titre"], ascending=[False, True], na_position="last")
    catalog = catalog.drop(columns=["sort_date"])

    catalog["Pages"] = catalog["Pages"].round().astype("Int64")
    return catalog


def records_to_json(catalog: pd.DataFrame) -> str:
    records: list[dict[str, object]] = []
    for row in catalog.to_dict(orient="records"):
        cleaned_row = {}
        for key, value in row.items():
            if pd.isna(value):
                cleaned_row[key] = ""
            else:
                cleaned_row[key] = value
        records.append(cleaned_row)
    return json.dumps(records, ensure_ascii=False).replace("</", "<\\/")


def build_html(catalog: pd.DataFrame) -> str:
    data_json = records_to_json(catalog)
    total_books = len(catalog)
    finished_books = int((catalog["Statut"] == "Fini").sum())
    in_progress_books = int((catalog["Statut"] == "En cours").sum())

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bibliotheque de lecture</title>
  <link rel="icon" href="data:image/svg+xml,&lt;svg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 100 100%27&gt;&lt;text y=%27.9em%27 font-size=%2790%27&gt;%F0%9F%93%9A%EF%B8%8F&lt;/text&gt;&lt;/svg&gt;">
  <link href="https://cdn.jsdelivr.net/npm/tabulator-tables@6.3.0/dist/css/tabulator.min.css" rel="stylesheet">
  <style>
    :root {{
      --page-bg: #131416;
      --panel-bg: rgba(24, 28, 32, 0.92);
      --panel-border: rgba(221, 205, 180, 0.12);
      --text: #f5efe4;
      --muted: #b6ab9e;
      --accent: #d18b59;
      --accent-dark: #9e6237;
      --finished-bg: rgba(90, 158, 128, 0.2);
      --finished-text: #9fe0be;
      --progress-bg: rgba(214, 142, 54, 0.18);
      --progress-text: #f1bc79;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--text);
      color-scheme: dark;
      background:
        radial-gradient(circle at top left, rgba(209, 139, 89, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(96, 125, 139, 0.16), transparent 26%),
        linear-gradient(135deg, #101214 0%, #171b20 42%, #1e252b 100%);
    }}

    .page {{
      width: min(1180px, calc(100% - 32px));
      margin: 32px auto;
    }}

    .hero {{
      display: grid;
      gap: 20px;
      padding: 28px;
      background: var(--panel-bg);
      border: 1px solid var(--panel-border);
      border-radius: 24px;
      box-shadow: 0 28px 64px rgba(0, 0, 0, 0.34);
      backdrop-filter: blur(8px);
    }}

    .hero-copy h1 {{
      margin: 0 0 10px;
      font-size: clamp(2rem, 5vw, 3.5rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }}

    .hero-copy p {{
      margin: 0;
      max-width: 64ch;
      color: var(--muted);
      line-height: 1.55;
      font-size: 1rem;
    }}

    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}

    .stat-card {{
      padding: 16px 18px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(221, 205, 180, 0.08);
    }}

    .stat-label {{
      display: block;
      color: var(--muted);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .stat-value {{
      font-size: clamp(1.8rem, 4vw, 2.7rem);
      line-height: 1;
    }}

    .toolbar {{
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin: 24px 0 16px;
      flex-wrap: wrap;
    }}

    .toolbar h2 {{
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
    }}

    .toolbar-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .filter-toggle {{
      border: 1px solid rgba(221, 205, 180, 0.12);
      background: rgba(255, 255, 255, 0.05);
      color: var(--text);
      border-radius: 999px;
      padding: 10px 16px;
      font: inherit;
      cursor: pointer;
      transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
    }}

    .filter-toggle.active {{
      background: var(--accent);
      border-color: var(--accent);
      color: #16181b;
    }}

    .search-box {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(221, 205, 180, 0.12);
      border-radius: 999px;
      width: min(100%, 360px);
    }}

    .search-box input {{
      width: 100%;
      border: 0;
      background: transparent;
      outline: none;
      font: inherit;
      color: var(--text);
    }}

    .search-box input::placeholder {{
      color: var(--muted);
    }}

    #book-table {{
      overflow: auto;
      border-radius: 20px;
      border: 1px solid rgba(221, 205, 180, 0.12);
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
      background: rgba(22, 25, 29, 0.96);
    }}

    .tabulator {{
      border: 0;
      background: transparent;
      font-size: 0.95rem;
      color: var(--text);
    }}

    .tabulator .tabulator-header {{
      border-bottom: 1px solid rgba(221, 205, 180, 0.08);
      background: rgba(31, 35, 40, 0.98);
    }}

    .tabulator .tabulator-col {{
      background: transparent;
      border-right: 0;
    }}

    .tabulator .tabulator-col-title,
    .tabulator .tabulator-cell {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .tabulator .tabulator-row {{
      border-bottom: 1px solid rgba(221, 205, 180, 0.06);
      background: transparent;
    }}

    .tabulator .tabulator-row.tabulator-row-even {{
      background: rgba(255, 255, 255, 0.02);
    }}

    .tabulator .tabulator-footer {{
      border-top: 1px solid rgba(221, 205, 180, 0.08);
      background: rgba(31, 35, 40, 0.96);
      color: var(--muted);
    }}

    .tabulator .tabulator-page,
    .tabulator .tabulator-page-size {{
      color: var(--text);
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(221, 205, 180, 0.1);
    }}

    .tabulator .tabulator-page.active {{
      background: var(--accent);
      color: #16181b;
    }}

    .tabulator input,
    .tabulator select {{
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
      border: 1px solid rgba(221, 205, 180, 0.12);
    }}

    .status-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 88px;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    .status-pill.finished {{
      color: var(--finished-text);
      background: var(--finished-bg);
    }}

    .status-pill.progress {{
      color: var(--progress-text);
      background: var(--progress-bg);
    }}

    .footer-note {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.9rem;
    }}

    @media (max-width: 720px) {{
      .page {{
        width: min(100% - 20px, 1180px);
        margin: 20px auto;
      }}

      .hero {{
        padding: 22px;
      }}

      .stats {{
        grid-template-columns: 1fr;
      }}

      .toolbar {{
        align-items: stretch;
      }}

      .toolbar-actions {{
        width: 100%;
      }}

      .search-box {{
        width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="hero-copy">
        <h1>Bibliotheque de lecture</h1>
        <p>Catalogue statique genere a partir des exports ebook et de la liste papier/audio. Tri, filtre et pagination fonctionnent directement dans le navigateur, sans backend.</p>
      </div>

      <div class="stats">
        <article class="stat-card">
          <span class="stat-label">Livres</span>
          <strong class="stat-value">{total_books}</strong>
        </article>
        <article class="stat-card">
          <span class="stat-label">Finis</span>
          <strong class="stat-value">{finished_books}</strong>
        </article>
        <article class="stat-card">
          <span class="stat-label">En cours</span>
          <strong class="stat-value">{in_progress_books}</strong>
        </article>
      </div>
    </section>

    <section>
      <div class="toolbar">
        <h2>Liste des bouquins</h2>
        <div class="toolbar-actions">
          <button id="filter-read" class="filter-toggle" type="button" aria-pressed="false">Lu</button>
          <label class="search-box" for="table-search">
            <span>Recherche</span>
            <input id="table-search" type="search" placeholder="Titre, auteur, categorie...">
          </label>
        </div>
      </div>
      <div id="book-table"></div>
      <p class="footer-note">La colonne statut est derivee automatiquement : ebook termine si le pourcentage lu atteint 90 %, sinon en cours. Les entrees papier/audio sont considerees comme finies.</p>
    </section>
  </main>

  <script src="https://cdn.jsdelivr.net/npm/tabulator-tables@6.3.0/dist/js/tabulator.min.js"></script>
  <script>
    const bookData = {data_json};

    const statusFormatter = (cell) => {{
      const value = cell.getValue() || "";
      const cssClass = value === "Fini" ? "finished" : "progress";
      return `<span class="status-pill ${{cssClass}}">${{value}}</span>`;
    }};

    const table = new Tabulator("#book-table", {{
      data: bookData,
      layout: "fitDataTable",
      responsiveLayout: false,
      pagination: true,
      paginationSize: 50,
      paginationSizeSelector: [25, 50, 100],
      movableColumns: true,
      initialSort: [
        {{ column: "Date de lecture", dir: "desc" }},
      ],
      columns: [
        {{ title: "Titre", field: "Titre", width: 320, headerFilter: true, tooltip: true }},
        {{ title: "Auteur(s)", field: "Auteurs", minWidth: 180, headerFilter: true }},
        {{ title: "Categorie", field: "Catégorie", minWidth: 150, headerFilter: true }},
        {{ title: "Statut", field: "Statut", width: 130, formatter: statusFormatter, hozAlign: "center", headerFilter: "list", headerFilterParams: {{ valuesLookup: true, clearable: true }} }},
        {{ title: "Pages", field: "Pages", width: 110, hozAlign: "right", sorter: "number" }},
        {{ title: "Date lecture", field: "Date de lecture", width: 140, sorter: "date" }},
      ],
    }});

    const searchInput = document.getElementById("table-search");
    const readFilterButton = document.getElementById("filter-read");
    let showReadOnly = false;

    const applyTopFilters = () => {{
      const query = searchInput.value.toLowerCase().trim();
      if (!query && !showReadOnly) {{
        table.clearFilter();
        return;
      }}

      table.setFilter((data) => {{
        const matchesSearch = !query || Object.values(data).some((value) => String(value ?? "").toLowerCase().includes(query));
        const matchesRead = !showReadOnly || data["Statut"] === "Fini";
        return matchesSearch && matchesRead;
      }});
    }};

    searchInput.addEventListener("input", () => {{
      applyTopFilters();
    }});

    readFilterButton.addEventListener("click", () => {{
      showReadOnly = !showReadOnly;
      readFilterButton.classList.toggle("active", showReadOnly);
      readFilterButton.setAttribute("aria-pressed", String(showReadOnly));
      applyTopFilters();
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    catalog = build_catalog()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_html(catalog), encoding="utf-8")
    print(f"HTML generated: {OUTPUT_PATH}")
    print(f"Rows: {len(catalog)}")


if __name__ == "__main__":
    main()