import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 🔹 Caminho base: funciona no Python normal e no PyInstaller
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)  # executável
else:
    base_path = Path(__file__).parent  # Python normal

# 🔹 Pasta do perfil do WhatsApp
USER_DATA_DIR = base_path / "perfil_whatsapp"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 🔹 Número e mensagem
numero = "556996041447"
mensagem = "Teste automático 🚀"

# 🔹 Caminho do Chromium para cada SO
import platform
so = platform.system().lower()
if so == "linux":
    CHROMIUM_EXECUTABLE = str(base_path / "playwright_browsers/chrome-linux64/chrome")
elif so == "windows":
    CHROMIUM_EXECUTABLE = str(base_path / "playwright_browsers/chrome-win32/chrome.exe")
elif so == "darwin":  # macOS
    CHROMIUM_EXECUTABLE = str(base_path / "playwright_browsers/chrome-mac/Chromium.app/Contents/MacOS/Chromium")
else:
    raise Exception(f"SO não suportado: {so}")

# 🔹 Função principal
def enviar_mensagem():
    print("🚀 Abrindo navegador com Playwright...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            executable_path=CHROMIUM_EXECUTABLE
        )
        page = context.new_page()

        print("🔹 Carregando WhatsApp Web...")
        page.goto("https://web.whatsapp.com/")
        page.wait_for_selector("div#app", timeout=0)
        print("✅ WhatsApp carregado!")

        print(f"🔹 Abrindo conversa do número {numero}...")
        page.goto(f"https://web.whatsapp.com/send?phone={numero}")
        caixa = page.locator("footer div[contenteditable='true']").first
        caixa.wait_for(timeout=0)

        print("🔹 Digitando mensagem...")
        caixa.click()
        caixa.type(mensagem, delay=50)

        print("🔹 Enviando mensagem...")
        page.keyboard.press("Enter")
        print("📩 Mensagem enviada!")

        time.sleep(3)
        print("✅ Processo concluído.")

# 🔹 Executa
if __name__ == "__main__":
    enviar_mensagem()