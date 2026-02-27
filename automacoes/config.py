import sys
import os
from pathlib import Path

# Configurações de Ambiente
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

if getattr(sys, 'frozen', False):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(__file__).parent

USER_DATA_DIR = BASE_PATH / "perfil_sicoobnet_persistente"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Constantes de Tempo
HEADLESS = False
TEMPO_MAXIMO_LOGIN = 180
URL_SICOOB = "https://www.sicoob.com.br/sicoobnet"