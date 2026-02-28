import time
from datetime import datetime, timedelta
import os
from config import TEMPO_MAXIMO_LOGIN

def esperar_login(page):
    """
    Detecta login concluído focando nos elementos mais estáveis do dashboard real.
    Prioriza IDs fixos e texto visível.
    """
    print("🔎 Aguardando confirmação de login no dashboard...")
    inicio = time.time()

    # Lista priorizada: primeiro o mais confiável
    selectors_logado = [
        "#layoutDashboard",               # 1. Raiz do dashboard (melhor)
        "#header",                        # 2. Header fixo
        "#idImagemFundoUsuario",          # 3. Foto de perfil (confirma auth completa)
        "button.userInfo",                # 4. Botão de usuário
        "div:has-text('Olá,')",           # 5. Saudação visível
    ]

    while time.time() - inicio < TEMPO_MAXIMO_LOGIN:
        try:
            # Tenta esperar QUALQUER um deles (OR com pipe)
            combined = " | ".join(selectors_logado)
            page.wait_for_selector(combined, state="visible", timeout=10000)
            
            # Se encontrou, loga qual foi e retorna sucesso
            print(f"✅ Detectado: {combined}")
            print("✅ Área logada confirmada!")
            time.sleep(2)  # folga para o resto carregar
            return True

        except Exception as e:
            # Trata timeout ou erro genérico sem importar classes específicas
            print(f"   Ainda aguardando... ({str(e)[:80]})")

        time.sleep(4)

    print("❌ Tempo esgotado sem detectar dashboard logado.")
    return False
    
def listar_contas(page):
    """
    Abre a seção de troca de contas e extrai diretamente do <select>
    apenas o número da conta (sem nome/titular) + index + value interno.
    """
    print("📂 Carregando lista de contas via dropdown...")

    # Clique em "Trocar conta" (mantemos robusto)
    trocar_selector = (
        "a.texto-trocar-conta, "
        "span.texto-header:has-text('Trocar conta'), "
        "a:has-text('Trocar conta'), "
        "img[alt*='troca conta'], img[src*='icone_troca_conta']"
    )
    try:
        page.locator(trocar_selector).first.click(timeout=15000)
        print("   → Clique em 'Trocar conta' efetuado.")
        time.sleep(2)  # folga para modal/dropdown aparecer
    except Exception as e:
        print(f"⚠️ Falha no clique (pode já estar visível): {e}")

    # Selector do dropdown (baseado no seu HTML)
    select_selector = (
        "#contaSelecionadaParaSerPrincipal, "
        "select.form-control, "
        "select[name*='contaSelecionada'], "
        "select:has(option[value='0'])"
    )

    print("   Aguardando dropdown de contas...")
    try:
        page.wait_for_selector(select_selector, state="visible", timeout=40000)
        print("   → Dropdown localizado!")
    except Exception as e:
        print(f"❌ Não encontrou o select: {e}")
        return []

    # Pega o select
    select = page.locator(select_selector).first

    # Todas as options
    options = select.locator("option").all()
    total_options = len(options)
    print(f"🔢 Total de opções encontradas: {total_options}")

    lista_contas = []
    for idx, opt in enumerate(options):
        try:
            value = opt.get_attribute("value") or ""
            numero = opt.inner_text().strip()

            # Ignora inválidas/default
            if not numero or value == "0" or "Nenhuma" in numero or "nenhuma conta" in numero.lower():
                continue

            lista_contas.append({
                "index": len(lista_contas),  # 0, 1, 2... só as válidas
                "value": value,
                "numero": numero
            })

            print(f"📌 Conta {len(lista_contas)}: {numero} (value={value}, index interno={idx})")

        except Exception as e:
            print(f"   Erro na option {idx}: {e}")
            continue

    print(f"✅ Total de contas válidas: {len(lista_contas)}")
    return lista_contas

def acessar_extrato(page, conta):
    """
    Fluxo completo: busca conta → acessa conta → vai ao extrato → seleciona período → busca → exporta PDF → baixa arquivo → volta para lista.
    """
    numero = conta.get('numero', '').strip()
    if not numero:
        print("❌ Número da conta não encontrado.")
        return

    print(f"\n🚀 Processando extrato PDF para conta: {numero}")

    # 1. Abre tela "Lista de contas" se necessário
    if page.locator("h3:has-text('Lista de contas')").count() == 0:
        trocar_sel = "a.texto-trocar-conta, span.texto-header:has-text('Trocar conta'), a:has-text('Trocar conta')"
        try:
            page.locator(trocar_sel).first.click(timeout=15000)
            page.wait_for_selector("h3:has-text('Lista de contas')", timeout=40000)
            print("   → Tela 'Lista de contas' aberta.")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Falha ao abrir tela de troca: {e}")
            return

    # 2. Limpa busca anterior (botão X)
    try:
        page.locator("button:has-text('X'), ib-sicoob-button[label='X']").first.click(timeout=5000)
        print("   → Busca anterior limpa.")
        time.sleep(1)
    except:
        pass

    # 3. Busca pela conta específica
    busca_sel = "input.sicoob-input-text, input[placeholder*='Buscar por tipo da conta']"
    try:
        input_busca = page.locator(busca_sel).first
        input_busca.fill(numero)
        input_busca.press("Enter")
        print(f"   → Busca por '{numero}' realizada.")
        time.sleep(4)  # aguarda filtro
    except Exception as e:
        print(f"❌ Falha na busca: {e}")
        return

    # 4. Verifica se a conta apareceu filtrada
    conta_row_sel = f"div.seletor-conta:has-text('{numero}')"
    if page.locator(conta_row_sel).count() == 0:
        print(f"❌ Conta {numero} não apareceu após busca.")
        return

    # 5. Clica em "Acessar conta"
    acessar_sel = "div.info-acesso-conta:has-text('Acessar conta'), div.content-acesso-conta"
    try:
        page.locator(conta_row_sel).locator(acessar_sel).first.click(timeout=15000)
        print("   → Clicou em 'Acessar conta'.")
    except:
        try:
            page.locator(conta_row_sel).first.click(timeout=10000)
            print("   → Clicou na row inteira (fallback).")
        except Exception as e:
            print(f"❌ Falha ao acessar conta: {e}")
            return

    # 6. Aguarda dashboard da conta
    print("⏳ Aguardando dashboard...")
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
        page.wait_for_selector("#layoutDashboard, div:has-text('Olá,'), header#header", timeout=30000)
        print("   → Dashboard carregado.")
        time.sleep(3)
    except:
        print("⚠️ Dashboard demorou, prosseguindo.")

    # 7. Acessa tela de extrato
    print("📄 Acessando tela de extrato...")
    extrato_found = False
    selectors_extrato = [
        "div:has-text('Extrato')",
        "div.novo:has-text('Extrato')",
        "a.clickable:has-text('Extrato de conta corrente')",
        "div.card:has-text('Extrato')"
    ]
    for sel in selectors_extrato:
        try:
            page.locator(sel).first.click(timeout=12000)
            print(f"   → Extrato clicado via {sel}")
            extrato_found = True
            break
        except:
            continue

    if not extrato_found:
        try:
            page.locator("i.icone-conta.clickable").first.click(timeout=12000)
            page.locator("a:has-text('Extrato de conta corrente')").click(timeout=12000)
            print("   → Extrato via menu lateral.")
            extrato_found = True
        except Exception as e:
            print(f"❌ Falha ao acessar extrato: {e}")
            return

    # 8. Aguarda tela de extrato carregar (confirmação por elementos específicos)
    print("⏳ Aguardando extrato carregar...")
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
        page.wait_for_selector(
            "div:has-text('Movimentações'), table.ui-table-tbody, div.movimentacoes, div.extrato-container",
            timeout=20000
        )
        print("   → Tela de extrato carregada com sucesso.")
        time.sleep(3)
    except:
        print("⚠️ Extrato aberto, mas tabela não detectada imediatamente.")

    # 9. Preenche período (últimos 30 dias - ajuste se quiser outro intervalo)
    periodo_selector = "input.sicoob-input-date, input[placeholder*='Período'], input.ib-sicoob-input-date"
    try:
        hoje = datetime.now()
        inicio = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
        fim = hoje.strftime("%d/%m/%Y")
        periodo_text = f"{inicio} - {fim}"

        input_periodo = page.locator(periodo_selector).first
        input_periodo.fill(periodo_text)
        print(f"   → Período preenchido: {periodo_text}")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Falha ao preencher período: {e}. Prosseguindo sem filtro de data.")

    # 10. Clica em "Buscar" para atualizar extrato com período
    buscar_sel = "button:has-text('Buscar'), .new-btn-sicoob:has-text('Buscar')"
    try:
        page.locator(buscar_sel).first.click(timeout=15000)
        page.wait_for_load_state("networkidle", timeout=20000)
        print("   → Busca por período realizada.")
        time.sleep(4)
    except Exception as e:
        print(f"⚠️ Falha ao clicar em Buscar: {e}")

    # 11. Abre modal de exportar
    exportar_sel = "span.clickable.ng-star-inserted:has-text('Exportar extrato'), button:has-text('Exportar extrato')"
    try:
        page.locator(exportar_sel).first.click(timeout=15000)
        page.wait_for_selector("div:has-text('Selecionar o formato desejado')", timeout=20000)
        print("   → Modal de exportar aberta.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Falha ao abrir modal de exportar: {e}")
        return

    # 12. Seleciona PDF
    pdf_radio = "input[type='radio'][value='PDF'], label:has-text('PDF'), span:has-text('PDF')"
    try:
        page.locator(pdf_radio).first.click(timeout=10000)
        print("   → PDF selecionado na modal.")
    except Exception as e:
        print(f"⚠️ Falha ao selecionar PDF: {e}")

    # 13. Clica em "Exportar extrato" e captura download
    exportar_btn = "button:has-text('Exportar extrato'), .new-btn-sicoob.primary:has-text('Exportar extrato')"
    try:
        with page.expect_download() as download_info:
            page.locator(exportar_btn).first.click(timeout=20000)
        
        download = download_info.value
        os.makedirs("extratos", exist_ok=True)
        caminho_arquivo = f"extratos/extrato_{numero}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        download.save_as(caminho_arquivo)
        print(f"   → PDF baixado com sucesso: {caminho_arquivo}")
    except Exception as e:
        print(f"❌ Falha ao exportar e baixar PDF: {e}")

    # 14. Fecha modal se ainda aberta
    try:
        page.locator("button:has-text('Cancelar'), .new-btn-sicoob:has-text('Cancelar')").first.click(timeout=8000)
        print("   → Modal fechada.")
    except:
        pass

    # 15. Volta para tela de lista de contas
    try:
        page.locator("a.texto-trocar-conta").first.click(timeout=15000)
        page.wait_for_selector("h3:has-text('Lista de contas')", timeout=25000)
        print("   → Voltou para 'Lista de contas'.")
    except:
        print("⚠️ Falha ao voltar para lista.")

    print(f"✅ Processo finalizado para {numero}")