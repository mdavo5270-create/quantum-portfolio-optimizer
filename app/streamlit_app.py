"""Interface Streamlit — Quantum Portfolio Optimizer

Fidèle à la maquette Phase 5 :
- Palette papier / encre / classique / recuit / avertissement
- Structure Protocole → Verdict → Réplication
- Axe de verdict A+B avec anti-chevauchement
- Disclaimer permanent

Lancement :
    streamlit run app/streamlit_app.py

Avertissement : ce n'est PAS un conseil financier.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon as MplPolygon

from src.data.market_data import prepare_data
from src.optimizer.cardinality import optimize_cardinality_from_returns
from src.optimizer.qaoa_portfolio import QAOAConfig, optimize_qaoa_from_returns
from src.optimizer.simulated_annealing import SAConfig
from src.backtest.engine import run_backtest
from src.optimizer.simulated_annealing import SAConfig as _SAConfig

# ── Design tokens (maquette) ──────────────────────────────────────────
PAPER = "#F3EDE3"
INK = "#1C1917"
RULE = "#D6CFC4"
CLASSIC = "#1F4D3A"
ANNEAL = "#9A6B2F"
WARN = "#7A2E2E"
MUTED = "#736B63"
CREAM = "#F7F3ED"

PRESETS = {
    "Diversifié 25": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX",
        "JPM", "BAC", "WFC", "GS",
        "JNJ", "PFE", "UNH", "ABBV",
        "PG", "KO", "PEP", "WMT",
        "XOM", "CVX", "CAT", "BA", "GE",
    ],
    "Tech 8": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX"],
    "Blue chips 6": ["AAPL", "MSFT", "JPM", "JNJ", "PG", "XOM"],
}

METHOD_META = {
    "markowitz": {"label": "Markowitz", "shape": "square", "color": CLASSIC, "symbol": "■"},
    "sa": {"label": "Recuit simulé", "shape": "diamond", "color": ANNEAL, "symbol": "◆"},
    "qaoa": {"label": "QAOA simulé", "shape": "circle", "color": WARN, "symbol": "○"},
}


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        html, body, [data-testid="stApp"] {{
            background-color: {PAPER} !important;
            color: {INK};
            font-family: 'IBM Plex Sans', sans-serif;
        }}
        h1, h2, h3, .fraunces {{
            font-family: 'Fraunces', Georgia, serif !important;
            color: {INK} !important;
            font-weight: 700 !important;
        }}
        .block-container {{ padding-top: 1.5rem; max-width: 960px; }}
        [data-testid="stSidebar"] {{
            background-color: {CREAM} !important;
            border-right: 1px solid {RULE};
        }}
        .disclaimer {{
            background: #F5EBE8;
            border-top: 2px solid {WARN};
            color: {WARN};
            padding: 0.65rem 1rem;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 1.25rem;
        }}
        .nav-line {{
            border-bottom: 1px solid {RULE};
            padding-bottom: 0.4rem;
            margin-bottom: 1rem;
            font-size: 0.95rem;
            color: {MUTED};
        }}
        .nav-line strong {{ color: {INK}; }}
        .verdict-sentence {{
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1.35rem;
            line-height: 1.4;
            color: {INK};
            margin: 0.5rem 0 1.25rem 0;
        }}
        .proof-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        .proof-table th {{
            text-align: left;
            color: {MUTED};
            font-weight: 500;
            border-bottom: 1px solid {RULE};
            padding: 0.4rem 0.5rem;
        }}
        .proof-table td {{
            padding: 0.45rem 0.5rem;
            border-bottom: 1px solid {RULE};
            color: {INK};
        }}
        .marginalia {{
            color: {MUTED};
            font-size: 0.85rem;
            border-left: 2px solid {RULE};
            padding-left: 0.75rem;
            margin-top: 1rem;
        }}
        div[data-testid="stButton"] > button {{
            background-color: {CLASSIC} !important;
            color: {PAPER} !important;
            border: none !important;
            border-radius: 2px !important;
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-weight: 600 !important;
        }}
        /* hide streamlit chrome noise */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def disclaimer() -> None:
    st.markdown(
        '<div class="disclaimer">Simulation expérimentale — <strong>ce n\'est pas un conseil financier</strong>. '
        "Aucun ordre réel n'est exécuté. Résultats historiques uniquement.</div>",
        unsafe_allow_html=True,
    )


def nav(active: str) -> None:
    items = ["Protocole", "Verdict", "Réplication"]
    parts = []
    for it in items:
        if it == active:
            parts.append(f"<strong>{it}</strong>")
        else:
            parts.append(it)
    st.markdown(
        f'<div class="nav-line">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(parts)}</div>',
        unsafe_allow_html=True,
    )


def _axis_positions(sharpes: dict[str, float], width: float = 10.0, min_gap: float = 0.45) -> dict[str, float]:
    """Map Sharpe → x on [0, width], with anti-overlap (order by sharpe desc)."""
    # Higher Sharpe → more classical (left)
    ordered = sorted(sharpes.items(), key=lambda kv: -kv[1])
    if not ordered:
        return {}
    vals = np.array([s for _, s in ordered], dtype=float)
    lo, hi = float(vals.min()), float(vals.max())
    span = max(hi - lo, 1e-6)
    # Map: best → left (0.1*width), worst → right (0.9*width)
    raw = {k: (0.1 + 0.8 * (hi - s) / span) * width for k, s in ordered}
    # Enforce min gap while preserving order (left to right = best to worst)
    xs = [raw[k] for k, _ in ordered]
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] < min_gap:
            xs[i] = xs[i - 1] + min_gap
    # If overflow, compress from right
    if xs[-1] > width * 0.95:
        overflow = xs[-1] - width * 0.95
        for i in range(len(xs)):
            xs[i] = max(width * 0.05, xs[i] - overflow * (i / max(len(xs) - 1, 1)))
        # re-enforce gap
        for i in range(1, len(xs)):
            if xs[i] - xs[i - 1] < min_gap:
                xs[i] = xs[i - 1] + min_gap
    return {ordered[i][0]: xs[i] for i in range(len(ordered))}


def draw_verdict_axis(results: dict[str, dict]) -> None:
    """Axe A+B : continuum + rangs + formes a11y + anti-chevauchement."""
    sharpes = {k: v["sharpe"] for k, v in results.items()}
    ranks = {
        k: i + 1
        for i, (k, _) in enumerate(sorted(sharpes.items(), key=lambda kv: -kv[1]))
    }
    positions = _axis_positions(sharpes, width=10.0, min_gap=0.55)

    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=140)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    y0 = 0.0
    ax.plot([0, 10], [y0, y0], color=INK, lw=1.8, solid_capstyle="butt", zorder=1)
    ax.plot([0, 0], [-0.15, 0.15], color=INK, lw=1.5)
    ax.plot([10, 10], [-0.15, 0.15], color=INK, lw=1.5)
    ax.text(0, -0.55, "CLASSICAL", fontsize=9, color=CLASSIC, fontweight="600", ha="left")
    ax.text(10, -0.55, "EXPERIMENTAL", fontsize=9, color=ANNEAL, fontweight="600", ha="right")

    # Alternate labels above/below for tight clusters
    for i, (key, x) in enumerate(sorted(positions.items(), key=lambda kv: kv[1])):
        meta = METHOD_META[key]
        color = meta["color"]
        above = i % 2 == 0
        y_mark = 0.55 if above else -0.85
        y_text = 0.95 if above else -1.35

        # tick on axis
        ax.plot([x, x], [-0.12, 0.12], color=color, lw=2, zorder=2)

        # leader
        ax.plot([x, x], [0.12 if above else -0.12, y_mark], color=color, lw=0.8, alpha=0.7)

        if meta["shape"] == "square":
            ax.add_patch(
                FancyBboxPatch(
                    (x - 0.14, y_mark - 0.14),
                    0.28,
                    0.28,
                    boxstyle="square,pad=0",
                    facecolor=color,
                    edgecolor=color,
                    zorder=3,
                )
            )
        elif meta["shape"] == "diamond":
            ax.add_patch(
                MplPolygon(
                    [(x, y_mark + 0.18), (x + 0.16, y_mark), (x, y_mark - 0.18), (x - 0.16, y_mark)],
                    closed=True,
                    facecolor=color,
                    edgecolor=color,
                    zorder=3,
                )
            )
        else:
            ax.add_patch(
                Circle(
                    (x, y_mark),
                    0.15,
                    facecolor="none",
                    edgecolor=color,
                    linewidth=2.2,
                    zorder=3,
                )
            )

        label = f"{ranks[key]}  {meta['label']}  ·  {sharpes[key]:.2f}"
        ax.text(x, y_text, label, ha="center", va="center", fontsize=9, color=color, fontweight="600")
        if key == "qaoa" and ranks[key] == max(ranks.values()):
            ax.text(
                x,
                y_text - (0.35 if above else -0.35),
                "sous-performance mesurée",
                ha="center",
                fontsize=8,
                color=WARN,
                style="italic",
            )

    ax.set_xlim(-0.3, 10.3)
    ax.set_ylim(-1.9, 1.6)
    ax.axis("off")
    fig.tight_layout(pad=0.3)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def run_optimization(tickers: list[str], k: int, start: str, methods: list[str]) -> dict:
    prices, returns, report = prepare_data(tickers, start=start, verbose=False)
    if returns is None or returns.empty or returns.shape[1] < 2:
        return {"error": "Données insuffisantes.", "report": report}

    out: dict = {"report": report, "returns": returns, "results": {}}
    if "markowitz" in methods:
        r = optimize_cardinality_from_returns(
            returns, max_assets=k, method="markowitz", n_random_subsets=60, seed=42
        )
        out["results"]["markowitz"] = {
            "sharpe": r.sharpe,
            "vol": r.volatility,
            "ret": r.expected_return,
            "weights": r.weights,
            "message": r.message,
        }
    if "sa" in methods:
        r = optimize_cardinality_from_returns(
            returns,
            max_assets=k,
            method="sa",
            sa_config=SAConfig(n_steps=4000, seed=42, step_size=0.08),
        )
        out["results"]["sa"] = {
            "sharpe": r.sharpe,
            "vol": r.volatility,
            "ret": r.expected_return,
            "weights": r.weights,
            "message": r.message,
        }
    if "qaoa" in methods:
        r = optimize_qaoa_from_returns(
            returns,
            max_assets=k,
            config=QAOAConfig(p=2, max_assets=k, n_samples=256, n_restarts=3, seed=42),
        )
        out["results"]["qaoa"] = {
            "sharpe": r.sharpe,
            "vol": r.volatility,
            "ret": r.expected_return,
            "weights": r.weights,
            "message": r.message,
        }
    return out


def verdict_sentence(results: dict) -> str:
    if not results:
        return "Aucune méthode sélectionnée."
    best = max(results.items(), key=lambda kv: kv[1]["sharpe"])
    name = METHOD_META[best[0]]["label"]
    if best[0] in ("markowitz", "sa") and "qaoa" in results:
        if results["qaoa"]["sharpe"] < best[1]["sharpe"] - 0.05:
            return (
                f"Sur cet univers et ces contraintes, {name} l'emporte. "
                f"L'écart du QAOA est documenté (proxy QUBO + calibration)."
            )
    return f"Sur cette run, {name} obtient le meilleur Sharpe ({best[1]['sharpe']:.2f})."


def main() -> None:
    st.set_page_config(
        page_title="QPO — Banc d'essai",
        page_icon="◇",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    inject_css()

    if "page" not in st.session_state:
        st.session_state.page = "Protocole"
    if "run_data" not in st.session_state:
        st.session_state.run_data = None

    st.markdown(
        "# Quantum Portfolio Optimizer\n"
        "<p style='color:#736B63;margin-top:-0.5rem'>Comparer, pas recommander.</p>",
        unsafe_allow_html=True,
    )
    disclaimer()

    # Navigation buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Protocole", use_container_width=True):
            st.session_state.page = "Protocole"
    with c2:
        if st.button("Verdict", use_container_width=True):
            st.session_state.page = "Verdict"
    with c3:
        if st.button("Réplication", use_container_width=True):
            st.session_state.page = "Réplication"

    nav(st.session_state.page)
    page = st.session_state.page

    # ── PROTOCOLE ─────────────────────────────────────────────────────
    if page == "Protocole":
        st.markdown("## Conditions de l'expérience")
        preset = st.selectbox("Preset d'univers", list(PRESETS.keys()))
        default_tickers = ", ".join(PRESETS[preset])
        tickers_raw = st.text_area("Tickers (séparés par des virgules)", value=default_tickers, height=80)
        tickers = [t.strip().upper() for t in tickers_raw.replace("\n", ",").split(",") if t.strip()]

        col_a, col_b = st.columns(2)
        with col_a:
            k = st.slider("Cardinalité K (max actifs)", min_value=2, max_value=min(12, max(2, len(tickers))), value=min(5, max(2, len(tickers))))
            start = st.text_input("Date de début", value="2019-01-01")
        with col_b:
            methods = st.multiselect(
                "Méthodes",
                options=["markowitz", "sa", "qaoa"],
                default=["markowitz", "sa", "qaoa"],
                format_func=lambda m: METHOD_META[m]["symbol"] + " " + METHOD_META[m]["label"],
            )

        st.markdown(
            '<p class="marginalia">Le protocole fixe les règles avant de voir les résultats. '
            "K limite le nombre d'actifs (contrainte discrète, NP-difficile).</p>",
            unsafe_allow_html=True,
        )

        if st.button("Lancer le banc d'essai", type="primary"):
            if len(tickers) < 2:
                st.error("Au moins 2 tickers requis.")
            elif not methods:
                st.error("Sélectionnez au moins une méthode.")
            else:
                with st.spinner("Téléchargement des données et optimisation…"):
                    try:
                        data = run_optimization(tickers, k, start, methods)
                        if "error" in data:
                            st.error(data["error"])
                        else:
                            st.session_state.run_data = data
                            st.session_state.page = "Verdict"
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Erreur : {exc}")

    # ── VERDICT ───────────────────────────────────────────────────────
    elif page == "Verdict":
        data = st.session_state.run_data
        if not data or not data.get("results"):
            st.info("Aucune run disponible. Configurez un protocole puis lancez le banc d'essai.")
        else:
            results = data["results"]
            report = data.get("report")
            if report is not None:
                st.caption(
                    f"Actifs chargés : {len(report.succeeded)} réussis"
                    + (f", {len(report.failed)} en échec" if report.failed else "")
                )

            st.markdown(
                f'<p class="verdict-sentence">{verdict_sentence(results)}</p>',
                unsafe_allow_html=True,
            )
            draw_verdict_axis(results)

            # Proof table
            rows = []
            for key, r in sorted(results.items(), key=lambda kv: -kv[1]["sharpe"]):
                meta = METHOD_META[key]
                active = r["weights"][r["weights"] > 1e-4].sort_values(ascending=False)
                assets = ", ".join(f"{a}" for a in active.index[:6])
                rows.append(
                    f"<tr><td>{meta['symbol']} {meta['label']}</td>"
                    f"<td>{r['sharpe']:.2f}</td>"
                    f"<td>{r['vol']:.1%}</td>"
                    f"<td>{r['ret']:.1%}</td>"
                    f"<td>{assets}</td></tr>"
                )
            st.markdown(
                "<table class='proof-table'><thead><tr>"
                "<th>Méthode</th><th>Sharpe</th><th>Vol</th><th>Rend. esp.</th><th>Actifs</th>"
                "</tr></thead><tbody>"
                + "".join(rows)
                + "</tbody></table>",
                unsafe_allow_html=True,
            )

            if "qaoa" in results:
                st.markdown(
                    '<p class="marginalia">QAOA : le proxy QUBO est faiblement corrélé au vrai Sharpe '
                    "(voir docs/methode_qaoa.md). La sous-performance éventuelle n'est pas masquée.</p>",
                    unsafe_allow_html=True,
                )

            # Weights detail
            with st.expander("Allocations détaillées"):
                for key, r in results.items():
                    meta = METHOD_META[key]
                    w = r["weights"][r["weights"] > 1e-4].sort_values(ascending=False)
                    st.markdown(f"**{meta['symbol']} {meta['label']}**")
                    st.dataframe(
                        pd.DataFrame({"poids": w.map(lambda x: f"{x:.1%}")}),
                        use_container_width=True,
                    )

    # ── RÉPLICATION ───────────────────────────────────────────────────
    elif page == "Réplication":
        data = st.session_state.run_data
        if not data or data.get("returns") is None:
            st.info("Lancez d'abord une optimisation depuis Protocole.")
        else:
            returns: pd.DataFrame = data["returns"]
            st.markdown("## Réplication historique")
            st.caption("Walk-forward hors échantillon — la performance passée n'annonce pas la future.")

            window = st.selectbox(
                "Fenêtre",
                [
                    "Tout l'historique disponible",
                    "2018–2020",
                    "2020–2022",
                    "2022–2025",
                ],
            )
            slice_map = {
                "2018–2020": ("2018-01-01", "2020-12-31"),
                "2020–2022": ("2020-01-01", "2022-12-31"),
                "2022–2025": ("2022-01-01", "2025-12-31"),
            }
            rets = returns
            if window in slice_map:
                a, b = slice_map[window]
                rets = returns.loc[a:b]

            if len(rets) < 320:
                st.warning("Pas assez de jours dans cette fenêtre pour un walk-forward robuste.")
            else:
                if st.button("Lancer la réplication", type="primary"):
                    with st.spinner("Backtest walk-forward…"):
                        curves = {}
                        metrics_rows = []
                        for method in ("markowitz", "sa"):
                            if method not in data["results"]:
                                continue
                            try:
                                bt = run_backtest(
                                    rets,
                                    method=method,
                                    train_days=252,
                                    test_days=63,
                                    sa_config=_SAConfig(n_steps=1500, seed=42),
                                )
                                curves[method] = bt.equity_curve
                                m = bt.metrics
                                metrics_rows.append(
                                    {
                                        "Méthode": METHOD_META[method]["symbol"]
                                        + " "
                                        + METHOD_META[method]["label"],
                                        "Sharpe": round(m.sharpe, 2),
                                        "Vol. ann.": f"{m.annualized_volatility:.1%}",
                                        "Max DD": f"{m.max_drawdown:.1%}",
                                        "Rend. ann.": f"{m.annualized_return:.1%}",
                                    }
                                )
                            except Exception as exc:
                                st.warning(f"{method}: {exc}")

                        if curves:
                            fig, ax = plt.subplots(figsize=(9, 4), dpi=130)
                            fig.patch.set_facecolor(PAPER)
                            ax.set_facecolor(PAPER)
                            for method, curve in curves.items():
                                ax.plot(
                                    curve.index,
                                    curve.values,
                                    color=METHOD_META[method]["color"],
                                    lw=1.8,
                                    label=METHOD_META[method]["label"],
                                )
                            ax.set_ylabel("Valeur (base 1)")
                            ax.legend(frameon=False)
                            ax.spines["top"].set_visible(False)
                            ax.spines["right"].set_visible(False)
                            ax.spines["left"].set_color(RULE)
                            ax.spines["bottom"].set_color(RULE)
                            ax.tick_params(colors=MUTED)
                            fig.tight_layout()
                            st.pyplot(fig, use_container_width=True)
                            plt.close(fig)
                            st.dataframe(pd.DataFrame(metrics_rows), use_container_width=True, hide_index=True)

            st.markdown(
                '<p class="marginalia">Le QAOA n\'est pas rejoué en walk-forward ici (coût de calibration). '
                "Comparaison hors échantillon centrée sur Markowitz vs recuit simulé.</p>",
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
