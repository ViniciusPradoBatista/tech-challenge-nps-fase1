"""
Funções de visualização com padrão visual único para todos os gráficos.

Os gráficos são pensados para público NÃO técnico: títulos que contam a
conclusão ("o quê"), eixos em português e poucas cores com significado fixo.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from src import config


def set_plot_style() -> None:
    """Aplica o estilo padrão a todos os gráficos do projeto."""
    plt.rcParams.update({
        "figure.figsize": (10, 5),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 11,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "font.size": 11,
    })


def save_figure(fig, file_name: str) -> None:
    """Salva a figura em reports/figures para uso no README e na apresentação."""
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIGURES_DIR / file_name)


def summarize_by_group(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """
    Resume, para cada grupo, a nota média, o % de detratores, o % de promotores
    e o NPS do grupo. É a tabela base de quase todos os gráficos da EDA.
    """
    summary = (
        df.groupby(group_column, observed=True)
        .agg(
            pedidos=(config.TARGET_SCORE, "size"),
            nota_media=(config.TARGET_SCORE, "mean"),
            pct_detratores=(config.NPS_CATEGORY, lambda s: (s == "Detrator").mean() * 100),
            pct_promotores=(config.NPS_CATEGORY, lambda s: (s == "Promotor").mean() * 100),
        )
        .round(2)
    )
    summary["nps"] = (summary["pct_promotores"] - summary["pct_detratores"]).round(1)
    return summary


def plot_score_and_detractors(summary: pd.DataFrame, title: str, x_label: str, ax=None):
    """
    Gráfico combinado: barras = % de detratores; linha = nota média.
    Facilita enxergar "pontos de ruptura" (onde a curva despenca).
    """
    if ax is None:
        _, ax = plt.subplots()
    positions = range(len(summary))
    labels = [str(i) for i in summary.index]

    ax.bar(positions, summary["pct_detratores"], color=config.COLOR_DETRACTOR, alpha=0.75, label="% detratores")
    ax.set_ylim(0, 105)
    ax.set_ylabel("% de detratores")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels)
    ax.set_xlabel(x_label)

    ax_score = ax.twinx()
    ax_score.plot(positions, summary["nota_media"], color=config.COLOR_PRIMARY, marker="o", linewidth=2.5, label="Nota média")
    ax_score.set_ylim(0, 10)
    ax_score.set_ylabel("Nota média (0-10)")
    ax_score.grid(False)
    ax_score.spines["right"].set_visible(True)

    for x, y in zip(positions, summary["nota_media"]):
        ax_score.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 8),
                          ha="center", color=config.COLOR_PRIMARY, fontweight="bold")

    ax.set_title(title)
    handles = ax.get_legend_handles_labels()[0] + ax_score.get_legend_handles_labels()[0]
    ax.legend(handles, ["% detratores", "Nota média"], loc="upper left", frameon=False)
    return ax
