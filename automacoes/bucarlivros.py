import threading
import os
import sys
from tkinter import *
from tkinter import messagebox
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path

# ==============================
# 🔧 Ajuste para Executável
# ==============================
if getattr(sys, 'frozen', False):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

# ==============================
# 📂 Pasta Downloads
# ==============================
PASTA_DOWNLOAD = Path("downloads")
PASTA_DOWNLOAD.mkdir(exist_ok=True)

# ==============================
# 🚀 Função da Automação
# ==============================
def executar_automacao(termo, quantidade):
    try:
        log("🚀 Iniciando navegador invisível...")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            log("🌐 Acessando site...")
            page.goto("https://www.baixelivros.com.br/", timeout=60000)

            log("🔎 Pesquisando livro...")
            page.fill("input.search-field", termo.strip())
            page.keyboard.press("Enter")

            page.wait_for_selector("a.titulo", timeout=30000)

            url_busca = page.url
            livros = page.locator("a.titulo")
            total = min(int(quantidade), livros.count())

            log(f"📚 Encontrados {total} livros para baixar...")

            for i in range(total):
                log(f"\n📖 Processando livro {i+1}")

                livros = page.locator("a.titulo")
                titulo = livros.nth(i).inner_text().strip()
                log(f"📘 {titulo}")

                livros.nth(i).click()

                # 🔥 ESSENCIAL para funcionar
                page.wait_for_load_state("networkidle")

                log("📥 Baixando PDF...")

                try:
                    with page.expect_download(timeout=60000) as download_info:
                        page.locator("#botaodownloadoriginal").click()

                    download = download_info.value
                    caminho_final = PASTA_DOWNLOAD / download.suggested_filename
                    download.save_as(caminho_final)

                    log(f"✅ Baixado: {download.suggested_filename}")

                except PlaywrightTimeoutError:
                    log("⚠️ Timeout no download, pulando...")

                page.goto(url_busca)
                page.wait_for_selector("a.titulo", timeout=30000)

            browser.close()
            log("\n🎉 Processo concluído com sucesso!")

    except Exception as e:
        log("❌ Erro geral:")
        log(str(e))


# ==============================
# 🖥️ Interface
# ==============================
def iniciar():
    termo = entry_termo.get().strip()
    qtd_str = entry_qtd.get().strip()

    if not termo or not qtd_str:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    try:
        qtd = int(qtd_str)
        if qtd < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Erro", "Quantidade deve ser número inteiro positivo.")
        return

    thread = threading.Thread(
        target=executar_automacao,
        args=(termo, qtd),
        daemon=True
    )
    thread.start()


def log(texto):
    caixa_texto.insert(END, texto + "\n")
    caixa_texto.see(END)


# ==============================
# 🎨 Janela Principal
# ==============================
janela = Tk()
janela.title("📚 Baixa Livros Automático")
janela.geometry("680x520")
janela.resizable(False, False)

Label(janela, text="Autor ou Nome do Livro:", font=("Arial", 12)).pack(pady=(20, 5))
entry_termo = Entry(janela, width=50, font=("Arial", 12))
entry_termo.pack(pady=5)

Label(janela, text="Quantidade de livros:", font=("Arial", 12)).pack(pady=(15, 5))
entry_qtd = Entry(janela, width=10, font=("Arial", 12))
entry_qtd.pack(pady=5)

Button(
    janela,
    text="🚀 Iniciar Downloads",
    font=("Arial", 13, "bold"),
    bg="#4CAF50",
    fg="white",
    command=iniciar,
    width=25,
    height=2
).pack(pady=25)

caixa_texto = Text(
    janela,
    height=16,
    width=78,
    font=("Consolas", 10),
    bg="#f8f9fa"
)
caixa_texto.pack(pady=10, padx=10)

scroll = Scrollbar(janela, command=caixa_texto.yview)
caixa_texto.configure(yscrollcommand=scroll.set)
scroll.pack(side=RIGHT, fill=Y)

janela.mainloop()