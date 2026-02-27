import sys
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# 🔒 FORÇA USAR O CHROMIUM EMPACOTADO NO EXE
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

# 📁 Base compatível com PyInstaller
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).parent

# 📁 Pasta persistente do perfil
USER_DATA_DIR = base_path / "perfil_sicoobnet_persistente"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 📦 Caminho da extensão (se usar)
EXTENSION_PATH = None  # Ex: str(base_path / "extensao_sicoob")

HEADLESS = False
PAUSA_APOS_LOGIN = 180


def acessar_sicoobnet():
    print("🚀 Iniciando Chromium embutido...")

    with sync_playwright() as p:
        context = None
        try:
            args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--enable-extensions",
                # 🔐 User-Agent compatível com Windows
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            ]

            if EXTENSION_PATH:
                args += [
                    f"--disable-extensions-except={EXTENSION_PATH}",
                    f"--load-extension={EXTENSION_PATH}",
                ]

            context = p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=HEADLESS,
                args=args,
                ignore_default_args=[
                    "--enable-automation",
                    "--disable-extensions"
                ],
                viewport=None,
                ignore_https_errors=True,
                java_script_enabled=True,
            )

            page = context.new_page()

            # 🔐 Remove navigator.webdriver
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            print("🔹 Abrindo SicoobNet...")
            page.goto(
                "https://www.sicoob.com.br/sicoobnet",
                timeout=120000,
                wait_until="domcontentloaded"
            )

            if not HEADLESS:
                print("\n⚠️ Faça login manual se necessário...")
                time.sleep(PAUSA_APOS_LOGIN)

            page.screenshot(path="sicoobnet_status.png")

            try:
                page.wait_for_selector(
                    "nav, [class*='menu'], div[class*='saldo'], .dashboard",
                    timeout=45000
                )
                print("✅ Login detectado com sucesso!")
            except PlaywrightTimeoutError:
                print("⚠️ Dashboard não detectado.")

            time.sleep(5)

        except Exception as e:
            print(f"❌ Erro: {str(e)}")

        finally:
            if context:
                context.close()
            print("🛑 Processo finalizado.")


if __name__ == "__main__":
    acessar_sicoobnet()