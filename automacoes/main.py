from playwright.sync_api import sync_playwright
from config import URL_SICOOB
from browser_manager import iniciar_navegador
import sicoob_actions as sicoob

def executar_bot():
    print("🚀 Iniciando sistema...")
    
    with sync_playwright() as p:
        context, page = iniciar_navegador(p)
        
        try:
            page.goto(URL_SICOOB, timeout=120000, wait_until="domcontentloaded")

            if not sicoob.esperar_login(page):
                print("❌ Tempo de login esgotado.")
                return

            minhas_contas = sicoob.listar_contas(page)


            for conta in minhas_contas:
                sicoob.acessar_extrato(page, conta)
                
                # Lógica de download ou leitura de dados entraria aqui
                # Volta para a lista de contas
                page.locator("a.texto-trocar-conta").click()
                page.wait_for_selector("div.seletor-conta")

            print("\n🏁 Processo finalizado com sucesso.")
            
            
        except Exception as e:
            print(f"💥 Erro crítico: {e}")
        finally:
            input("Pressione ENTER para fechar o navegador...")
            context.close()

if __name__ == "__main__":
    executar_bot()