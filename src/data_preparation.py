"""
Funções de carga, validação, tratamento e criação de variáveis (feature engineering).

Fluxo usado no notebook 01:
    raw_df = load_raw_data()
    quality_report = build_quality_report(raw_df)
    processed_df = prepare_dataset(raw_df)
    save_processed_data(processed_df)
"""
import numpy as np
import pandas as pd

from src import config


# --------------------------------------------------------------------------
# Carga e validação
# --------------------------------------------------------------------------
def load_raw_data(path=config.DATA_RAW_PATH) -> pd.DataFrame:
    """Lê o CSV original e confere se todas as colunas do dicionário existem."""
    raw_df = pd.read_csv(path)

    missing_columns = set(config.EXPECTED_COLUMNS) - set(raw_df.columns)
    if missing_columns:
        raise ValueError(f"Colunas ausentes na base: {sorted(missing_columns)}")

    return raw_df


def build_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera um resumo de qualidade por coluna: tipo, nulos, valores únicos,
    mínimo e máximo. Serve para documentar o estado da base antes do tratamento.
    """
    report = pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isna().sum(),
        "pct_nulos": (df.isna().mean() * 100).round(2),
        "valores_unicos": df.nunique(),
    })
    numeric_df = df.select_dtypes(include="number")
    report["minimo"] = numeric_df.min()
    report["maximo"] = numeric_df.max()
    return report


def check_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verifica regras de negócio que, se violadas, indicam possível erro de registro.
    Retorna uma tabela com a quantidade e o percentual de linhas afetadas.
    """
    rules = {
        "NPS fora da escala 0-10": ~df["nps_score"].between(0, 10),
        "CSAT fora da escala 0-10": ~df["csat_internal_score"].between(0, 10),
        "Valores negativos em colunas numéricas": (df.select_dtypes(include="number") < 0).any(axis=1),
        "Atraso maior que o tempo total de entrega": df["delivery_delay_days"] > df["delivery_time_days"],
        "Tempo de resolução > 0 sem nenhum contato com o SAC": (
            (df["customer_service_contacts"] == 0) & (df["resolution_time_days"] > 0)
        ),
        "Desconto maior que o valor do pedido": df["discount_value"] > df["order_value"],
        "Frete maior que o valor do pedido": df["freight_value"] > df["order_value"],
        "order_id duplicado": df["order_id"].duplicated(),
        "Linha totalmente duplicada": df.duplicated(),
    }
    summary = pd.DataFrame({
        "regra": list(rules.keys()),
        "linhas_afetadas": [int(mask.sum()) for mask in rules.values()],
    })
    summary["pct_da_base"] = (summary["linhas_afetadas"] / len(df) * 100).round(2)
    return summary


def count_iqr_outliers(df: pd.DataFrame, columns) -> pd.DataFrame:
    """Conta outliers pelo critério do intervalo interquartil (1,5 x IQR)."""
    rows = []
    for column in columns:
        q1, q3 = df[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        is_outlier = (df[column] < lower) | (df[column] > upper)
        rows.append({
            "coluna": column,
            "limite_inferior": round(lower, 2),
            "limite_superior": round(upper, 2),
            "qtd_outliers": int(is_outlier.sum()),
            "pct_outliers": round(is_outlier.mean() * 100, 2),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Tratamento e criação de variáveis
# --------------------------------------------------------------------------
def classify_nps(score: pd.Series) -> pd.Series:
    """Converte a nota 0-10 na categoria oficial do NPS."""
    categories = np.select(
        [score < config.NPS_DETRACTOR_MAX, score < config.NPS_PROMOTER_MIN],
        ["Detrator", "Neutro"],
        default="Promotor",
    )
    return pd.Series(
        pd.Categorical(categories, categories=["Detrator", "Neutro", "Promotor"], ordered=True),
        index=score.index,
    )


def calculate_nps(score: pd.Series) -> float:
    """NPS = % promotores - % detratores (varia de -100 a +100)."""
    category = classify_nps(score)
    pct_promoters = (category == "Promotor").mean()
    pct_detractors = (category == "Detrator").mean()
    return round((pct_promoters - pct_detractors) * 100, 1)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria variáveis derivadas, todas disponíveis ANTES da pesquisa de NPS.
    Elas facilitam a leitura de negócio na EDA e podem ajudar o modelo.
    """
    df = df.copy()

    # --- Alvos ---
    df[config.NPS_CATEGORY] = classify_nps(df[config.TARGET_SCORE])
    df[config.TARGET_DETRACTOR] = (df[config.NPS_CATEGORY] == "Detrator").astype(int)

    # --- Logística ---
    df["has_delay"] = (df["delivery_delay_days"] > 0).astype(int)
    df["delay_bucket"] = pd.cut(
        df["delivery_delay_days"], bins=[-1, 0, 1, 2, 3, np.inf],
        labels=["Sem atraso", "1 dia", "2 dias", "3 dias", "4+ dias"],
    )

    # --- Pedido (valores relativos são mais comparáveis do que absolutos) ---
    df["discount_pct"] = (df["discount_value"] / df["order_value"]).round(4)
    df["freight_pct"] = (df["freight_value"] / df["order_value"]).round(4)
    df["ticket_per_item"] = (df["order_value"] / df["items_quantity"]).round(2)

    # --- Atendimento ---
    df["has_service_contact"] = (df["customer_service_contacts"] > 0).astype(int)
    df["complaints_bucket"] = pd.cut(
        df["complaints_count"], bins=[-1, 1, 3, 5, np.inf],
        labels=["0-1", "2-3", "4-5", "6+"],
    )

    # --- Perfil do cliente ---
    df["age_group"] = pd.cut(
        df["customer_age"], bins=[17, 29, 39, 49, 59, 120],
        labels=["18-29", "30-39", "40-49", "50-59", "60+"],
    )
    df["tenure_group"] = pd.cut(
        df["customer_tenure_months"], bins=[0, 12, 36, 72, np.inf],
        labels=["Até 1 ano", "1-3 anos", "3-6 anos", "6+ anos"],
    )

    # --- Flags de qualidade (mantemos as linhas, mas sinalizamos) ---
    df["flag_delay_gt_delivery_time"] = (df["delivery_delay_days"] > df["delivery_time_days"]).astype(int)
    df["flag_resolution_without_contact"] = (
        (df["customer_service_contacts"] == 0) & (df["resolution_time_days"] > 0)
    ).astype(int)
    df["flag_discount_gt_order_value"] = (df["discount_value"] > df["order_value"]).astype(int)

    return df


def prepare_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline completo de tratamento:
      1. remove duplicidades (por segurança, mesmo que a base não tenha);
      2. padroniza textos da coluna de região;
      3. garante tipos numéricos;
      4. cria variáveis derivadas e flags de qualidade.

    Decisão importante: NÃO removemos outliers nem linhas inconsistentes.
    Pedidos de alto valor são reais no e-commerce, e as inconsistências afetam
    poucas linhas. Em vez de apagar, sinalizamos com flags para análise.
    """
    df = raw_df.drop_duplicates().drop_duplicates(subset="order_id").copy()
    df["customer_region"] = df["customer_region"].astype(str).str.strip().str.title()

    numeric_columns = [c for c in config.EXPECTED_COLUMNS if c != "customer_region"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    return add_features(df)


def save_processed_data(df: pd.DataFrame, path=config.DATA_PROCESSED_PATH) -> None:
    """Salva a base tratada para ser reutilizada pela EDA e pelo modelo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_processed_data(path=config.DATA_PROCESSED_PATH) -> pd.DataFrame:
    """Lê a base tratada e restaura a ordem das variáveis categóricas."""
    df = pd.read_csv(path)
    ordered_categories = {
        config.NPS_CATEGORY: ["Detrator", "Neutro", "Promotor"],
        "delay_bucket": ["Sem atraso", "1 dia", "2 dias", "3 dias", "4+ dias"],
        "complaints_bucket": ["0-1", "2-3", "4-5", "6+"],
        "age_group": ["18-29", "30-39", "40-49", "50-59", "60+"],
        "tenure_group": ["Até 1 ano", "1-3 anos", "3-6 anos", "6+ anos"],
    }
    for column, categories in ordered_categories.items():
        df[column] = pd.Categorical(df[column], categories=categories, ordered=True)
    return df
