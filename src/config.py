"""
Configurações centrais do projeto: caminhos, nomes de colunas e regras de negócio.

Centralizar essas definições evita "números mágicos" espalhados pelos notebooks
e garante que todas as etapas (tratamento, EDA e modelo) usem as mesmas regras.
"""
from pathlib import Path

# --------------------------------------------------------------------------
# Caminhos do projeto (resolvidos a partir da raiz do repositório)
# --------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "desafio_nps_fase_1.csv"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "nps_tratado.csv"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

RANDOM_STATE = 42  # semente fixa para garantir reprodutibilidade

# --------------------------------------------------------------------------
# Colunas da base original (dicionário de dados do enunciado)
# --------------------------------------------------------------------------
ID_COLUMNS = ["customer_id", "order_id"]

TARGET_SCORE = "nps_score"            # nota 0-10 (alvo da regressão)
TARGET_DETRACTOR = "is_detractor"     # 1 = detrator (alvo da classificação)
NPS_CATEGORY = "nps_category"         # detrator / neutro / promotor

CUSTOMER_COLUMNS = ["customer_age", "customer_region", "customer_tenure_months"]
ORDER_COLUMNS = ["order_value", "items_quantity", "discount_value", "payment_installments"]
LOGISTICS_COLUMNS = ["delivery_time_days", "delivery_delay_days", "freight_value", "delivery_attempts"]
SERVICE_COLUMNS = ["customer_service_contacts", "resolution_time_days", "complaints_count"]

# Variáveis coletadas DEPOIS (ou junto) da pesquisa de NPS.
# Elas não podem entrar no modelo preditivo, pois não existem no momento em que
# queremos prever a nota -> risco de vazamento de dados (data leakage).
POST_SURVEY_COLUMNS = ["csat_internal_score", "repeat_purchase_30d"]

EXPECTED_COLUMNS = (
    ID_COLUMNS
    + CUSTOMER_COLUMNS
    + ORDER_COLUMNS
    + LOGISTICS_COLUMNS
    + SERVICE_COLUMNS
    + [TARGET_SCORE]
    + POST_SURVEY_COLUMNS
)

# --------------------------------------------------------------------------
# Regra oficial do NPS (escala 0-10)
#   0 a 6  -> Detrator | 7 e 8 -> Neutro | 9 e 10 -> Promotor
# A base traz notas com casas decimais (ex.: 6.9), então usamos limites
# contínuos: nota < 7 é detrator, 7 <= nota < 9 é neutro, nota >= 9 é promotor.
# --------------------------------------------------------------------------
NPS_DETRACTOR_MAX = 7.0   # limite superior (exclusivo) para detrator
NPS_PROMOTER_MIN = 9.0    # limite inferior (inclusivo) para promotor

# Paleta usada em todos os gráficos (mesma cor = mesmo significado)
COLOR_DETRACTOR = "#D64545"
COLOR_NEUTRAL = "#E8A33D"
COLOR_PROMOTER = "#2E9E6A"
COLOR_PRIMARY = "#2F5D8A"
COLOR_MUTED = "#9AA5B1"
