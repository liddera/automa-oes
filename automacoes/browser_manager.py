from playwright.sync_api import sync_playwright
from config import USER_DATA_DIR, HEADLESS

def iniciar_navegador(p):
    """
    Configura e lança o navegador Chromium com parâmetros de persistência
    e técnicas para evitar a detecção de automação (anti-bot).
    """
    print("🌐 Configurando motor do navegador...")

    # Cria ou carrega um contexto persistente. 
    # Isso faz com que cookies, cache e logins fiquem salvos na pasta definida.
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR), # Pasta onde o perfil do Chrome será salvo
        headless=HEADLESS,                # Se True, roda escondido. Se False, mostra a janela.
        args=[
            "--no-sandbox",                # Necessário para rodar em alguns ambientes Linux/Docker
            "--disable-dev-shm-usage",      # Evita erros de memória compartilhada em containers
            "--disable-blink-features=AutomationControlled", # Remove a bandeira de "automatizado" do navegador
            "--start-maximized",           # Abre a janela em tela cheia
        ],
        # Remove argumentos padrão que o Playwright usa e que sites de bancos costumam rastrear
        ignore_default_args=["--enable-automation", "--disable-extensions"],
        viewport=None, # Permite que o navegador use o tamanho real da janela (maximizada)
    )
    
    # Cria uma nova aba (página) dentro do contexto configurado
    page = context.new_page()
    
    # 🛡️ INJEÇÃO DE SCRIPT ANTI-DETECÇÃO
    # Muitos sites verificam a propriedade 'navigator.webdriver'. 
    # Este script "esconde" essa propriedade definindo-a como undefined.
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    print("✅ Navegador inicializado e pronto para uso.")
    return context, page