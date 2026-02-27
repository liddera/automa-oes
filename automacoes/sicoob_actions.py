import time
from config import TEMPO_MAXIMO_LOGIN

def esperar_login(page):
    """
    Monitora a página até que os elementos exclusivos da área logada 
    (como o seletor de contas) apareçam na tela.
    """
    print("🔎 Aguardando login manual do usuário...")
    inicio = time.time()
    
    while time.time() - inicio < TEMPO_MAXIMO_LOGIN:
        try:
            # Verifica se o elemento que contém as contas já existe no DOM
            if page.locator("div.seletor-conta").count() > 0:
                print("✅ Login detectado com sucesso!")
                return True
        except: 
            pass # Ignora erros momentâneos de carregamento
        
        time.sleep(3) # Intervalo para não sobrecarregar a CPU
        
    print("❌ Tempo limite de login excedido.")
    return False

def listar_contas(page):
    """
    Navega até a tela de seleção de contas, ajusta a paginação para 
    exibir todas e mapeia os dados (nome e número) de cada conta.
    """
    print("📂 Navegando para a tela de troca de contas...")
    # Clica no link do topo para alternar entre empresas/contas
    page.locator("a.texto-trocar-conta").click()
    
    # Aguarda o título da modal/página para garantir que carregou
    page.wait_for_selector("h3:has-text('Lista de contas')", timeout=60000)

    print("⚙️ Ajustando visualização para 200 itens por página...")
    try:
        # Tenta expandir o dropdown de paginação e selecionar o máximo (200)
        page.locator("div.ui-dropdown").last.click()
        page.locator("li", has_text="200").click()
        page.wait_for_load_state("networkidle") # Aguarda as requisições terminarem
    except Exception as e:
        print(f"⚠️ Não foi possível ajustar a paginação (pode haver poucas contas): {e}")

    # Localiza todas as linhas de conta na tabela
    contas_elementos = page.locator("tbody.ui-table-tbody div.seletor-conta")
    total = contas_elementos.count()
    print(f"🔢 Total de contas encontradas: {total}")

    lista_contas = []
    for i in range(total):
        elemento = contas_elementos.nth(i)
        
        # Extrai o número da conta (ex: 12.345-6)
        numero = elemento.locator(".account_type .right span").inner_text().strip()
        
        # Extrai o nome do titular/empresa limpando o prefixo "Nome:"
        nome_bruto = elemento.locator(".text-info-conta", has_text="Nome:").inner_text()
        nome = nome_bruto.replace("Nome:", "").strip()
        
        lista_contas.append({
            "index": i, 
            "numero": numero, 
            "nome": nome
        })
        print(f"📌 Mapeada: {numero} | {nome}")

    return lista_contas

def acessar_extrato(page, conta):
    """
    Entra em uma conta específica, abre o menu lateral e clica no extrato.
    """
    print(f"\n🚀 Acessando conta: {conta['nome']} ({conta['numero']})")
    
    # Clica na conta baseada no índice mapeado anteriormente
    page.locator("div.seletor-conta").nth(conta["index"]).click()
    
    # Aguarda o Dashboard carregar
    print("⏳ Aguardando carregamento do painel principal...")
    page.wait_for_load_state("networkidle")
    
    # O ícone da maleta (Contas) é o gatilho para o menu de extrato
    print("🖱️ Abrindo menu lateral 'Contas'...")
    page.wait_for_selector("i.icone-conta.clickable", timeout=30000)
    page.locator("i.icone-conta.clickable").first.click()
    
    # Localiza e clica no link de Extrato de Conta Corrente
    print("📄 Clicando em 'Extrato de conta corrente'...")
    selector_extrato = "a.clickable:has-text('Extrato de conta corrente')"
    page.wait_for_selector(selector_extrato, timeout=15000)
    page.locator(selector_extrato).click()
    
    # Pequena pausa para garantir a renderização da tabela de extrato
    page.wait_for_load_state("networkidle")
    print(f"✅ Tela de extrato carregada para {conta['numero']}")
    time.sleep(2)