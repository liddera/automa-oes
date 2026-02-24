import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
import sys

# 🔹 Caminho base para PyInstaller compatível
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).parent

# 🔹 Pasta do perfil do WhatsApp
USER_DATA_DIR = base_path / "perfil_whatsapp"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 🔹 Número e mensagem
numero = "556993758751"
mensagem = "Teste automático 🚀"

# 🔹 Função para adicionar texto no painel
def log(text):
    txt_log.configure(state='normal')
    txt_log.insert(tk.END, text + "\n")
    txt_log.see(tk.END)
    txt_log.configure(state='disabled')
    root.update()

# 🔹 Função que executa os passos do WhatsApp
def enviar_mensagem():
    try:
        log("🚀 Abrindo navegador com Playwright...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=False
            )
            page = context.new_page()

            log("🔹 Carregando WhatsApp Web...")
            page.goto("https://web.whatsapp.com/")
            page.wait_for_selector("div#app", timeout=0)
            log("✅ WhatsApp carregado!")

            log(f"🔹 Abrindo conversa do número {numero}...")
            page.goto(f"https://web.whatsapp.com/send?phone={numero}")
            caixa_mensagem = page.locator("footer div[contenteditable='true']").first
            caixa_mensagem.wait_for(timeout=0)

            log("🔹 Preparando mensagem...")
            caixa_mensagem.click()
            caixa_mensagem.type(mensagem, delay=50)

            log("🔹 Enviando mensagem...")
            page.keyboard.press("Enter")
            log("📩 Mensagem enviada com sucesso!")

            time.sleep(3)
            log("✅ Processo concluído.")

    except Exception as e:
        messagebox.showerror("Erro", str(e))
        log(f"❌ Erro: {e}")

# 🔹 Interface Tkinter
root = tk.Tk()
root.title("Painel WhatsApp Automático")
root.geometry("500x400")

tk.Label(root, text="Painel de execução do WhatsApp", font=("Arial", 14)).pack(pady=10)

txt_log = scrolledtext.ScrolledText(root, state='disabled', width=60, height=20)
txt_log.pack(padx=10, pady=10)

tk.Button(root, text="Executar Passos", command=enviar_mensagem).pack(pady=10)

root.mainloop()