# Project Ares-Luna
## The Kepler 5

The web app currently runs a similarity algorithm between data on **Earth** (currently junk) and **Mars** (scraped from NASA databases and averaged).

### To run:

If `uv` is not installed, do so:
*Unix:*
```bash
curl -LsSf https://astral.sh | sh
```
*Windows:*
```powershell
powershell -c "irm https://astral.sh | iex"
```

Clone the repository if not done already, and sync the virtual environment via:
```bash
uv sync
```

To run:
```bash
uv run streamlit run app.py
```
