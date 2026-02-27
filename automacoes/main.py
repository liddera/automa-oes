import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Pasta persistente completa
base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).parent
USER_DATA_DIR = base_path / "perfil_sicoobnet_persistente"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

EXTENSION_PATH = None 
HEADLESS = False
PAUSA_APOS_LOGIN = 180 

def acessar_sicoobnet():
    # REMOVIDO: CHROME_EXECUTABLE (usaremos o nativo do Playwright)
    print("🚀 Iniciando CHROMIUM EMBUTIDO com permissão para extensões...")

    with sync_playwright() as p:
        try:
            args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "--enable-extensions", 
            ]

            if EXTENSION_PATH:
                args += [
                    f"--disable-extensions-except={EXTENSION_PATH}",
                    f"--load-extension={EXTENSION_PATH}",
                ]

            # AJUSTE: Removido executable_path para usar o bundle do Playwright
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=HEADLESS,
                # executable_path foi removido aqui
                args=args,
                # IMPORTANTE: Chromium embutido exige ignorar estas flags para permitir extensões
                ignore_default_args=["--enable-automation", "--disable-extensions"], 
                viewport={"width": 1366, "height": 768},
                ignore_https_errors=True,
                java_script_enabled=True,
            )

            page = context.new_page()

            print("🔹 Abrindo SicoobNet...")
            page.goto("https://www.sicoob.com.br/sicoobnet", timeout=120000, wait_until="domcontentloaded")

            if not HEADLESS:
                print(f"\n⚠️ Verifique se a extensão do Sicoob está ativa no Chromium embutido.")
                time.sleep(PAUSA_APOS_LOGIN)

            page.screenshot(path="sicoobnet_status.png")
            
            try:
                page.wait_for_selector(
                    "nav, [class*='menu'], div[class*='saldo'], .dashboard",
                    timeout=45000
                )
                print("✅ Logado com sucesso no Chromium embutido!")
            except PlaywrightTimeoutError:
                print("⚠️ Dashboard não detectado.")

            time.sleep(5)

        except Exception as e:
            print(f"❌ Erro: {str(e)}")
        finally:
            if 'context' in locals():
                context.close()
            print("🛑 Processo finalizado.")

if __name__ == "__main__":
    # Garanta que o chromium está instalado rodando no terminal: playwright install chromium
    acessar_sicoobnet()
