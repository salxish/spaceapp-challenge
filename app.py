from pathlib import Path

import streamlit as st
from PIL import Image

from similarity import DEFAULT_METRICS, METRICS, load_earth, load_mars, score

st.set_page_config(
    page_title="Terrain Comparison",
    layout="wide",
)

ASSETS = Path("assets")
EARTH_IMAGE = ASSETS / "makgadikgadi.jpg"
MARS_IMAGE = ASSETS / "jezero.webp"

st.markdown(
    """
<style>
    .block-container {
        padding-top: 1.5rem;
        max-width: 100%;
    }

    .stApp {
        background-color: #101010;
    }

    h1, h2, h3, p, label {
        color: white;
    }

    [data-testid="stImage"] {
        width: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)


def format_value(value, unit):
    if value is None:
        return "n/a"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    unit_str = f" {unit}" if unit else ""
    return f"{value}{unit_str}"


earth = load_earth()
mars = load_mars()

st.title("Terrain Comparison")
st.caption("Earth ↔ Mars | Makgadikgadi ↔ Jezero Crater")

left, middle, right = st.columns([2, 2, 1.5], gap="medium")

with left:
    st.subheader("Earth — Makgadikgadi")
    st.image(Image.open(EARTH_IMAGE).convert("RGB"), use_container_width=True)
    rows = []
    for key, spec in METRICS.items():
        rows.append({"Metric": spec["label"], "Value": format_value(earth.get(key), spec["unit"])})
    st.table(rows)

with middle:
    st.subheader("Mars — Jezero Crater")
    st.image(Image.open(MARS_IMAGE).convert("RGB"), use_container_width=True)
    rows = []
    for key, spec in METRICS.items():
        rows.append({"Metric": spec["label"], "Value": format_value(mars.get(key), spec["unit"])})
    st.table(rows)

with right:
    st.markdown("**Similarity analysis**")

    selected = st.multiselect(
        "Metrics to include",
        options=list(METRICS),
        default=DEFAULT_METRICS,
        format_func=lambda k: METRICS[k]["label"],
    )
    
    if not selected:
        st.info("Select at least one metric to compute similarity.")
    else:
        result = score(earth, mars, selected)

        if result["score"] is None:
            st.info("Awaiting data.")
        else:
            st.metric("Similarity score", f"{result['score']}/100")
            st.progress(result["score"] / 100)

        st.markdown("**Per-metric breakdown**")
        for item in result["breakdown"]:
            st.markdown(f"**{item['label']}**")
            if item["available"]:
                st.caption(
                    f"Earth: {format_value(item['earth'], item['unit'])} | "
                    f"Mars: {format_value(item['mars'], item['unit'])} | "
                    f"Similarity: {round(item['similarity'] * 100, 1)}%"
                )
                st.progress(item["similarity"])
            else:
                st.caption(
                    f"Earth: {format_value(item['earth'], item['unit'])} | "
                    f"Mars: {format_value(item['mars'], item['unit'])} | Similarity: n/a"
                )
                st.progress(0.0)


        if result["missing"]:
            st.caption("Unavailable metrics: " + ", ".join(result["missing"]))
