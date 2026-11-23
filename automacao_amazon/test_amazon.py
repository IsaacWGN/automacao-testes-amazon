# -*- coding: utf-8 -*-
"""
Scripts de teste automatizados - Amazon Brasil
Documento de origem: "Definição dos Casos de Teste - Amazon" (CT_001 a CT_010)

Seguem as boas práticas da Aula 6:
  * Selenium + Python + unittest (o Selenium não traz estrutura de teste);
  * um método por caso de teste, comentado com os passos do documento;
  * espera implícita (implicitly_wait) + pausas (time.sleep) entre passos;
  * Select para campos <select> (ex.: "Classificar por").

Somente os casos marcados "Automatizado = Sim" foram automatizados:
CT_001, CT_002, CT_003, CT_004, CT_005, CT_006 e CT_009.
"""

import re
import shutil
import tempfile
import unittest

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import config
from base import TesteAmazonBase, criar_driver, preco_para_float, By, WebDriverWait


class TestesAmazonBrasil(TesteAmazonBase):

    # =========================================================================
    # CT_001 - Navegar por departamento pelo menu "Todos"
    # =========================================================================
    def test_CT_001_navegar_por_departamento(self):
        self.abrir()

        # Passo 1 - Clicar no ícone de menu "Todos" (☰) no canto superior esquerdo
        self.passo(1, 'Clicar no menu "Todos"')
        self.driver.find_element(By.ID, "nav-hamburger-menu").click()
        menu = self.esperar_visivel(By.ID, "hmenu-content")
        self.verificar(menu is not None, "Menu lateral aberto")

        # Passo 2 - Clicar em "ver tudo", caso a lista de departamentos esteja recolhida
        self.passo(2, 'Expandir "ver tudo" se necessário')
        xp_depto = (f"//div[@id='hmenu-content']//a[contains(@class,'hmenu-item')]"
                    f"[normalize-space()='{config.DEPARTAMENTO}']")
        depto = self.driver.find_element(By.XPATH, xp_depto)
        if not depto.is_displayed():
            for link in self.driver.find_elements(
                    By.XPATH, "//div[@id='hmenu-content']//a[contains(@class,'hmenu-item')]"
                              "[translate(normalize-space(),'VT','vt')='ver tudo']"):
                if link.is_displayed():
                    link.click()
                    self.pausa(1)
                    break
        self.verificar(depto.is_displayed(), f'Departamento "{config.DEPARTAMENTO}" visível')

        # Passo 3 - Clicar no departamento "Computadores e Informática"
        self.passo(3, f'Clicar em "{config.DEPARTAMENTO}"')
        depto.click()
        self.pausa(1)
        xp_sub = (f"//ul[contains(@class,'hmenu-visible')]//a[normalize-space()='{config.SUBCATEGORIA}']")
        sub = self.esperar_visivel(By.XPATH, xp_sub)
        self.verificar(sub is not None, f'Submenu com a subcategoria "{config.SUBCATEGORIA}"')

        # Passo 4 - Clicar na subcategoria "Notebooks"
        self.passo(4, f'Clicar em "{config.SUBCATEGORIA}"')
        sub.click()
        self.pausa()
        self.tratar_bloqueios()
        self.verificar(config.SUBCATEGORIA in self.driver.title,
                       f'Página/título da categoria "{config.SUBCATEGORIA}"', self.driver.title)

        # Passo 5 - Verificar os 10 primeiros produtos exibidos
        self.passo(5, "Verificar se os 10 primeiros produtos são notebooks")
        self.js("window.scrollTo(0, document.body.scrollHeight / 3);")
        self.pausa(1)
        titulos = self.js("""
            const t = [...document.querySelectorAll('a[href*="/dp/"]')]
              .map(a => (a.innerText || a.getAttribute('aria-label') || '').trim().replace(/\\s+/g,' '))
              .filter(s => s.length > 15 && !s.startsWith('R$'));
            return [...new Set(t)].slice(0, 10);""")
        padrao = re.compile(r"notebook|laptop|chromebook|macbook|galaxy book|ultrabook", re.I)
        fora = [t for t in titulos if not padrao.search(t)]
        self.verificar(len(titulos) > 0, "Produtos listados na categoria", "nenhum produto encontrado")
        self.verificar(not fora, "Somente notebooks na listagem", "; ".join(fora)[:300])

        # Passo 6 - Clicar no botão "Voltar" do navegador
        self.passo(6, 'Clicar em "Voltar" no navegador')
        self.driver.back()
        self.pausa()
        self.verificar(self.existe(By.ID, "twotabsearchtextbox"),
                       "Página anterior carregada sem erro")

        # Passo 7 - Abrir novamente o menu "Todos" e clicar no "X" de fechar
        self.passo(7, 'Abrir o menu e fechar no "X"')
        url_antes = self.driver.current_url
        self.driver.find_element(By.ID, "nav-hamburger-menu").click()
        self.pausa(1)
        self.esperar_visivel(By.ID, "hmenu-close-icon").click()
        self.pausa(1)
        fechado = self.js("""
            const c = document.getElementById('hmenu-canvas');
            const r = document.getElementById('hmenu-content').getBoundingClientRect();
            return (c && c.className.includes('translateX-left')) || r.right <= 0;""")
        self.verificar(fechado, "Menu fechado")
        self.verificar(self.driver.current_url == url_antes, "Página atual sem alteração")
        self.concluir()

    # =========================================================================
    # CT_002 - Filtrar resultados por faixa de preço e avaliação
    # =========================================================================
    def test_CT_002_filtrar_preco_e_avaliacao(self):
        self.abrir()

        # Passo 1 - Pesquisar "caixa de som bluetooth" na barra de pesquisa
        self.passo(1, f'Pesquisar "{config.TERMO_FILTROS}"')
        self.pesquisar(config.TERMO_FILTROS)
        self.verificar(len(self.resultados(True)) > 0, "Página de resultados exibida")
        self.verificar(self.existe(By.ID, "reviewsRefinements"), "Filtros na lateral esquerda")

        # Passo 2 - Na seção "Avaliação dos clientes", clicar em "4 estrelas ou mais"
        self.passo(2, 'Aplicar filtro "4 estrelas ou mais"')
        self.driver.find_element(
            By.CSS_SELECTOR, "#reviewsRefinements a[aria-label*='Quatro estrelas']").click()
        self.pausa()
        self.verificar("p_72" in self.driver.current_url, "Filtro de avaliação aplicado")

        # Passo 3 - Verificar a avaliação dos 10 primeiros produtos
        self.passo(3, "Conferir avaliação >= 4 nos 10 primeiros")
        notas = self.js("""
            return [...document.querySelectorAll("[data-component-type='s-search-result']")]
              .slice(0, 10).map(r => {
                const a = r.querySelector("[aria-label*='de 5 estrelas'], .a-icon-alt");
                const t = a ? (a.getAttribute('aria-label') || a.textContent) : '';
                const m = t.match(/([0-9][.,][0-9])/);
                return m ? parseFloat(m[1].replace(',', '.')) : null; });""")
        abaixo = [n for n in notas if n is not None and n < 4]
        self.verificar(not abaixo, "Todas as notas >= 4", str(notas))

        # Passo 4 - Informar mínimo "100" e máximo "200"
        # Obs.: a interface atual usa um controle deslizante (slider) que grava os
        # valores nos campos ocultos "low-price" e "high-price" do formulário de preço.
        self.passo(4, "Aplicar faixa de preço R$ 100 a R$ 200")
        self.observar("Layout atual: faixa de preço por slider (sem campos mínimo/máximo e botão 'Ir').")
        self.js("""
            const lo = document.querySelector("input[name='low-price']");
            lo.value = arguments[0];
            lo.form.querySelector("input[name='high-price']").value = arguments[1];
            lo.form.submit();""", "100", "200")
        self.pausa(3)
        self.verificar("p_36" in self.driver.current_url, "Filtro de preço aplicado",
                       self.driver.current_url[:120])

        # Passo 5 - Verificar o preço dos 10 primeiros produtos
        self.passo(5, "Conferir preços entre R$ 100,00 e R$ 200,00")
        precos = [p["preco"] for p in self.precos_dos_resultados(10)]
        fora = [p for p in precos if p < 100 or p > 200]
        self.verificar(precos and not fora, "Preços dentro da faixa", str(precos))

        # Passo 6 - Informar mínimo "200" e máximo "100" (faixa invertida)
        self.passo(6, "Aplicar faixa invertida (200 a 100)")
        self.js("""
            const lo = document.querySelector("input[name='low-price']");
            lo.value = arguments[0];
            lo.form.querySelector("input[name='high-price']").value = arguments[1];
            lo.form.submit();""", "200", "100")
        self.pausa(3)
        sem_erro = "Amazon.com.br" in self.driver.title and len(self.resultados(True)) > 0
        self.verificar(sem_erro, "Faixa inválida tratada sem erro técnico", self.driver.title)
        if "p_36" not in self.driver.current_url:
            self.observar("Faixa invertida foi ignorada silenciosamente (nenhuma mensagem ao usuário).")

        # Passo 7 - Remover os filtros aplicados ("Limpar")
        self.passo(7, 'Remover filtros ("Limpar")')
        limpar = self.driver.find_elements(
            By.XPATH, "//div[@id='reviewsRefinements']//a[normalize-space()='Limpar']")
        if limpar:
            limpar[0].click()
            self.pausa()
        self.verificar("p_72" not in self.driver.current_url and "p_36" not in self.driver.current_url,
                       "Resultados sem filtros", self.driver.current_url[:120])
        self.concluir()

    # =========================================================================
    # CT_003 - Ordenar resultados por preço
    # =========================================================================
    def _ordenar(self, valor):
        select = Select(self.driver.find_element(By.ID, "s-result-sort-select"))
        select.select_by_value(valor)
        self.pausa(3)
        return Select(self.driver.find_element(By.ID, "s-result-sort-select")).first_selected_option.text

    @staticmethod
    def _fora_de_ordem(precos, crescente=True):
        """Retorna os pares vizinhos que quebram a ordenação."""
        erros = []
        for anterior, atual in zip(precos, precos[1:]):
            if (crescente and atual < anterior) or (not crescente and atual > anterior):
                erros.append(f"R$ {anterior:.2f} -> R$ {atual:.2f}")
        return erros

    def test_CT_003_ordenar_por_preco(self):
        self.abrir()

        # Passo 1 - Pesquisar "mouse sem fio" na barra de pesquisa
        self.passo(1, f'Pesquisar "{config.TERMO_ORDENACAO}"')
        self.pesquisar(config.TERMO_ORDENACAO)
        atual = Select(self.driver.find_element(By.ID, "s-result-sort-select")).first_selected_option.text
        self.verificar("destaque" in atual.lower(), 'Seletor "Classificar por: Em destaque"', atual)

        # Passo 2 - Clicar no seletor "Classificar por"
        self.passo(2, "Listar as opções de ordenação")
        opcoes = [o.text for o in Select(self.driver.find_element(By.ID, "s-result-sort-select")).options]
        self.verificar(any("menor para o maior" in o for o in opcoes)
                       and any("maior para o menor" in o for o in opcoes),
                       "Opções de ordenação por preço disponíveis", str(opcoes))

        # Passo 3 - Selecionar "Preço: menor para maior"
        self.passo(3, 'Selecionar "Preço: menor para maior"')
        texto = self._ordenar("price-asc-rank")
        self.verificar("menor para o maior" in texto, "Opção escolhida exibida no seletor", texto)

        # Passo 4 - Anotar os preços dos 10 primeiros produtos
        self.passo(4, "Conferir ordem crescente")
        precos = [p["preco"] for p in self.precos_dos_resultados(10)]
        erros = self._fora_de_ordem(precos, crescente=True)
        self.verificar(not erros, "Preços em ordem crescente",
                       f"{precos} | quebras: {', '.join(erros)}")

        # Passo 5 - Selecionar "Preço: maior para menor"
        self.passo(5, 'Selecionar "Preço: maior para menor"')
        texto = self._ordenar("price-desc-rank")
        self.verificar("maior para o menor" in texto, "Nova ordenação aplicada", texto)

        # Passo 6 - Anotar os preços dos 10 primeiros produtos
        self.passo(6, "Conferir ordem decrescente")
        pagina1 = self.precos_dos_resultados(60)
        precos = [p["preco"] for p in pagina1[:10]]
        erros = self._fora_de_ordem(precos, crescente=False)
        self.verificar(not erros, "Preços em ordem decrescente",
                       f"{precos} | quebras: {', '.join(erros)}")

        # Passo 7 - Avançar para a página 2 dos resultados
        self.passo(7, "Ir para a página 2 e conferir a ordenação")
        asins_p1 = {p["asin"] for p in pagina1}
        self.driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next").click()
        self.pausa(3)
        self.verificar("price-desc-rank" in self.driver.current_url, "Ordenação mantida na página 2")
        pagina2 = self.precos_dos_resultados(10)
        repetidos = [p["asin"] for p in pagina2 if p["asin"] in asins_p1]
        self.verificar(not repetidos, "Sem itens repetidos da página 1", str(repetidos))
        erros = self._fora_de_ordem([p["preco"] for p in pagina2], crescente=False)
        self.verificar(not erros, "Página 2 em ordem decrescente", ", ".join(erros))
        self.concluir()

    # =========================================================================
    # CT_004 - Selecionar variação de um produto (cor)
    # =========================================================================
    def _cor_selecionada(self):
        el = self.driver.find_elements(By.ID, "inline-twister-expanded-dimension-text-color_name")
        if el:
            return el[0].text.strip()
        el = self.driver.find_elements(By.CSS_SELECTOR, "#variation_color_name .selection")
        return el[0].text.strip() if el else ""

    def _preco_produto(self):
        return preco_para_float(self.js("""
            const a = document.querySelector('.priceToPay .a-offscreen');
            if (a && a.textContent.trim()) return a.textContent;
            const b = document.querySelector('#corePriceDisplay_desktop_feature_div .priceToPay, #corePrice_feature_div .a-offscreen');
            return b ? b.innerText || b.textContent : null;"""))

    def test_CT_004_selecionar_variacao_cor(self):
        self.abrir()

        # Passo 1 - Pesquisar "Echo Dot 5ª geração" e acessar a página do produto oficial
        self.passo(1, "Abrir a página do Echo Dot")
        self.pesquisar(config.TERMO_VARIACAO)
        link = self.js("""
            const r = [...document.querySelectorAll("[data-component-type='s-search-result']")]
              .find(x => /^Echo Dot/i.test((x.querySelector('h2')||{}).innerText||'')
                         && !/Max/i.test(x.querySelector('h2').innerText));
            const a = r && r.querySelector("a[href*='/dp/']");
            return a ? a.href : null;""")
        self.verificar(link is not None, "Produto Echo Dot encontrado na busca")
        self.driver.get(link)
        self.pausa()
        self.tratar_bloqueios()
        self.verificar(self.existe(By.ID, "twister_feature_div"), "Opções de cor disponíveis")

        # Passo 2 - Observar qual cor está selecionada por padrão
        self.passo(2, "Identificar a cor padrão")
        cor_inicial = self._cor_selecionada()
        url_inicial = self.driver.current_url
        self.verificar(bool(cor_inicial), "Uma cor destacada", cor_inicial)

        # Passo 3 - Selecionar outra cor (ex.: "Branco")
        self.passo(3, f'Selecionar a cor "{config.COR_VARIACAO}"')
        self.driver.find_element(
            By.XPATH, f"//div[@id='twister_feature_div']//img[@alt='{config.COR_VARIACAO}']").click()
        try:
            WebDriverWait(self.driver, 10).until(lambda d: self._cor_selecionada() == config.COR_VARIACAO)
        except Exception:
            pass
        self.pausa()
        self.verificar(self._cor_selecionada() == config.COR_VARIACAO,
                       f'Cor "{config.COR_VARIACAO}" exibida', self._cor_selecionada())
        if "Branc" not in self.driver.title:
            self.observar(f"Título da aba não acompanhou a troca de cor: '{self.driver.title[:90]}'")

        # Passo 4 - Conferir preço e disponibilidade após a troca
        self.passo(4, "Conferir preço e disponibilidade")
        preco = self._preco_produto()
        self.verificar(preco is not None and preco > 0, "Preço exibido para a variação", str(preco))
        self.verificar(self.existe(By.ID, "add-to-cart-button"), 'Disponível ("Adicionar ao carrinho")')

        # Passo 5 - Observar a barra de endereço do navegador
        self.passo(5, "Conferir a URL da variação")
        asin = lambda u: (re.search(r"/dp/([A-Z0-9]{10})", u) or [None, None])[1]
        self.verificar(asin(self.driver.current_url) != asin(url_inicial),
                       "Código do produto (ASIN) alterado na URL", self.driver.current_url[:100])

        # Passo 6 - Recarregar a página (F5)
        self.passo(6, "Recarregar a página")
        self.driver.refresh()
        self.pausa()
        self.verificar(self._cor_selecionada() == config.COR_VARIACAO,
                       "Cor mantida após recarregar", self._cor_selecionada())
        self.verificar(self._preco_produto() == preco, "Mesmo preço após recarregar")

        # Passo 7 - Selecionar uma variação marcada como indisponível, se houver
        self.passo(7, "Variação indisponível (se houver)")
        indisponiveis = self.driver.find_elements(
            By.XPATH, "//div[@id='twister_feature_div']//li[contains(@class,'unavailable')]")
        if not indisponiveis:
            self.observar("Nenhuma variação indisponível no momento - passo não aplicável.")
        else:
            indisponiveis[0].click()
            self.pausa()
            self.verificar(not self.existe(By.ID, "add-to-cart-button"),
                           "Compra direta não oferecida para variação indisponível")
        self.concluir()

    # =========================================================================
    # CT_005 - Filtrar ofertas e validar o percentual de desconto
    # =========================================================================
    def test_CT_005_ofertas_percentual_desconto(self):
        # Passo 1 - Acessar https://www.amazon.com.br/deals
        self.passo(1, "Acessar a página de ofertas")
        self.abrir(config.URL_OFERTAS)
        if "/deals" not in self.driver.current_url:
            self.observar(f"/deals redirecionou para {self.driver.current_url.split('?')[0]}")
        cards = self.esperar_visivel(By.CSS_SELECTOR, "[data-testid='product-card']")
        self.verificar(cards is not None, "Cards de ofertas exibidos")

        # Passo 2 - No filtro de departamento, selecionar "Eletrônicos"
        self.passo(2, f'Filtrar departamento "{config.DEPARTAMENTO_OFERTAS}"')
        botao = self.driver.find_element(
            By.XPATH, f"//button[normalize-space()='{config.DEPARTAMENTO_OFERTAS}']")
        self.js("arguments[0].scrollIntoView({block:'center'});", botao)
        botao.click()
        self.pausa(3)
        self.verificar("eletronicos" in self.driver.current_url.lower()
                       or self.existe(By.XPATH, "//*[normalize-space()='Filtrado por']"),
                       "Filtro de departamento aplicado", self.driver.current_url[:120])

        # Passo 3 - No filtro de desconto, selecionar a faixa "25% ou mais"
        # Obs.: o filtro atual é um slider; usamos as setas do teclado até 25%.
        self.passo(3, f"Definir desconto mínimo de {config.DESCONTO_MINIMO}%")
        slider = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='Desconto mínimo']")
        self.js("arguments[0].scrollIntoView({block:'center'});", slider)
        ActionChains(self.driver).move_to_element(slider).click().perform()
        alvo = f"{config.DESCONTO_MINIMO}%"
        for _ in range(100):
            if slider.get_attribute("aria-valuetext") == alvo:
                break
            atual = int(re.sub(r"\D", "", slider.get_attribute("aria-valuetext") or "0") or 0)
            slider.send_keys(Keys.ARROW_RIGHT if atual < config.DESCONTO_MINIMO else Keys.ARROW_LEFT)
        self.pausa(3)
        self.verificar(slider.get_attribute("aria-valuetext") == alvo,
                       f"Desconto mínimo = {alvo}", slider.get_attribute("aria-valuetext"))

        # Passo 4 - Verificar o selo de desconto dos 10 primeiros cards
        self.passo(4, "Conferir selos de desconto")
        selos = self.js("""
            return [...document.querySelectorAll("[data-testid='product-card']")].slice(0, 10)
              .map(c => { const m = c.innerText.match(/(\\d+)% off/); return m ? +m[1] : null; });""")
        abaixo = [s for s in selos if s is not None and s < config.DESCONTO_MINIMO]
        self.verificar(selos and not abaixo, f"Todos os selos >= {alvo}", str(selos))

        # Passo 5 - Anotar o preço do primeiro card e clicar nele
        self.passo(5, "Abrir a primeira oferta")
        primeiro = self.js("""
            const c = document.querySelector("[data-testid='product-card']");
            const a = c.querySelector("a[href*='/dp/']");
            const m = c.innerText.match(/Preço da Oferta:\\s*(R\\$\\s*[\\d\\.]+,\\d{2})/);
            return {href: a ? a.href : null, preco: m ? m[1] : null};""")
        preco_card = preco_para_float(primeiro["preco"])
        self.driver.get(primeiro["href"])   # abre na mesma aba (o card abre em nova aba)
        self.pausa()
        self.tratar_bloqueios()
        preco_pagina = self._preco_produto()
        self.verificar(preco_card == preco_pagina, "Mesmo preço do card",
                       f"card={preco_card} página={preco_pagina}")

        # Passo 6 - Localizar o preço anterior ("De:") e o percentual de desconto
        self.passo(6, 'Localizar preço "De:" e percentual')
        anterior = preco_para_float(self.js(
            "const e=document.querySelector('.basisPrice .a-offscreen'); return e?e.textContent:null;"))
        pct_txt = self.js("const e=document.querySelector('.savingsPercentage'); return e?e.textContent:null;")
        pct = int(re.sub(r"\D", "", pct_txt)) if pct_txt else None
        self.verificar(anterior and pct, "Preço anterior e percentual visíveis", f"De={anterior} pct={pct_txt}")

        # Passo 7 - Calcular (preço anterior - preço atual) / preço anterior x 100
        self.passo(7, "Validar o cálculo do desconto")
        if anterior and pct and preco_pagina:
            calculado = (anterior - preco_pagina) / anterior * 100
            self.verificar(abs(calculado - pct) <= 1, "Diferença <= 1 ponto percentual",
                           f"calculado={calculado:.2f}% exibido={pct}%")
            print(f"      = ({anterior:.2f} - {preco_pagina:.2f}) / {anterior:.2f} x 100 = {calculado:.2f}%")
        self.concluir()

    # =========================================================================
    # CT_006 - Alterar o idioma do site para inglês e retornar ao português
    # =========================================================================
    def test_CT_006_alterar_idioma(self):
        self.abrir()

        # Passo 1 - Observar o seletor de idioma no cabeçalho (bandeira do Brasil / "PT")
        self.passo(1, "Localizar o seletor de idioma")
        seletor = self.driver.find_elements(By.ID, "icp-nav-flyout")
        if not self.verificar(len(seletor) > 0, 'Seletor de idioma "PT" no cabeçalho',
                              "elemento #icp-nav-flyout inexistente"):
            # Caminho alternativo: página de preferências de idioma
            self.driver.get(config.URL_BASE + "customer-preferences/edit")
            self.pausa()
            radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            self.verificar(len(radios) > 0, "Opções de idioma na página de preferências",
                           f"página '{self.driver.title}' sem opções")
            self.concluir()          # não é possível prosseguir com os passos 2 a 7
            return

        # Passo 2 - Passar o mouse sobre o seletor de idioma
        self.passo(2, "Abrir as opções de idioma")
        ActionChains(self.driver).move_to_element(seletor[0]).perform()
        self.pausa(1)
        ingles = self.driver.find_elements(By.XPATH, "//a[contains(@href,'language=en')]|//span[contains(.,'English')]")
        self.verificar(len(ingles) > 0, 'Opção "English - EN"')

        # Passo 3 - Selecionar "English - EN"
        self.passo(3, 'Selecionar "English - EN"')
        ingles[0].click()
        self.pausa()
        salvar = self.driver.find_elements(By.ID, "icp-save-button")
        if salvar:
            salvar[0].click()
            self.pausa()

        # Passo 4 - Observar os textos do cabeçalho
        self.passo(4, "Conferir cabeçalho em inglês")
        cabecalho = self.driver.find_element(By.ID, "nav-link-accountList").text
        self.verificar("Hello" in cabecalho or "Account" in cabecalho, "Cabeçalho em inglês", cabecalho)

        # Passo 5 - Pesquisar "Kindle" e observar os preços
        self.passo(5, "Pesquisar e conferir moeda R$")
        self.pesquisar(config.TERMO_ENTREGA)
        moeda = self.js("const e=document.querySelector('.a-price .a-offscreen');return e?e.textContent:'';")
        self.verificar("R$" in moeda, "Preços continuam em reais", moeda)

        # Passo 6 - Abrir o carrinho pelo ícone do cabeçalho
        self.passo(6, "Abrir o carrinho")
        self.driver.find_element(By.ID, "nav-cart").click()
        self.pausa()
        self.verificar("Cart" in self.driver.page_source, "Carrinho em inglês")

        # Passo 7 - Retornar ao seletor e escolher "Português - PT"
        self.passo(7, 'Voltar para "Português - PT"')
        ActionChains(self.driver).move_to_element(
            self.driver.find_element(By.ID, "icp-nav-flyout")).perform()
        self.pausa(1)
        self.driver.find_element(By.XPATH, "//a[contains(@href,'language=pt')]").click()
        self.pausa()
        self.verificar("Olá" in self.driver.find_element(By.ID, "nav-link-accountList").text,
                       "Interface de volta ao português")
        self.concluir()

    # =========================================================================
    # CT_009 - Consultar disponibilidade de entrega por CEP
    # =========================================================================
    def _abrir_janela_cep(self):
        self.driver.find_element(By.ID, "nav-global-location-popover-link").click()
        self.esperar_visivel(By.ID, "GLUXZipUpdateInput_0")

    def _informar_cep(self, parte1, parte2):
        campo1 = self.driver.find_element(By.ID, "GLUXZipUpdateInput_0")
        campo2 = self.driver.find_element(By.ID, "GLUXZipUpdateInput_1")
        campo1.clear()
        campo1.send_keys(parte1)
        campo2.clear()
        campo2.send_keys(parte2)
        self.driver.find_element(By.ID, "GLUXZipUpdate").click()
        self.pausa()

    def _texto_local(self):
        el = self.driver.find_elements(By.ID, "glow-ingress-block")
        return el[0].text.replace("\n", " ") if el else ""

    def test_CT_009_entrega_por_cep(self):
        # Perfil próprio para conseguir "fechar e reabrir o navegador" no passo 7
        perfil = tempfile.mkdtemp(prefix="perfil_ct009_")
        self.driver.quit()
        self.driver = criar_driver(perfil)
        self.espera = WebDriverWait(self.driver, config.ESPERA_EXPLICITA)
        try:
            self.abrir()
            local_inicial = self._texto_local()

            # Passo 1 - Clicar em "Selecione o endereço" ("Enviar para") no cabeçalho
            self.passo(1, "Abrir a janela de localização")
            self._abrir_janela_cep()
            self.verificar(self.existe(By.ID, "GLUXZipUpdateInput_0"), 'Janela "Escolha sua localização"')

            # Passo 2 - Informar o CEP "00000-000" e clicar em "Confirmar"
            self.passo(2, "CEP 00000-000")
            self._informar_cep(*config.CEP_INVALIDO)
            erro = self.driver.find_element(By.ID, "GLUXZipError")
            self.verificar(erro.is_displayed(), "Mensagem de CEP inválido", erro.text)
            self.verificar(self._texto_local() == local_inicial, "Localização não alterada")

            # Passo 3 - Informar o CEP "abcde-fgh"
            self.passo(3, "CEP com letras")
            self._informar_cep(*config.CEP_LETRAS)
            aceitou = self.driver.find_element(By.ID, "GLUXZipUpdateInput_0").get_attribute("value")
            self.verificar(aceitou == "" or erro.is_displayed(),
                           "Letras recusadas ou mensagem de CEP inválido", f"campo='{aceitou}'")
            if aceitou:
                self.observar("O campo aceita letras; a validação ocorre só ao confirmar.")

            # Passo 4 - Informar o CEP válido "65075-441" (São Luís - MA)
            self.passo(4, "CEP válido 65075-441")
            self._informar_cep(*config.CEP_VALIDO)
            continuar = self.driver.find_elements(By.CSS_SELECTOR, "#GLUXConfirmClose, .a-popover-footer input")
            for b in continuar:
                if b.is_displayed():
                    b.click()
                    break
            self.pausa(3)
            self.driver.refresh()
            self.pausa()
            local = self._texto_local()
            self.verificar("65075" in local, "Cabeçalho com o CEP informado", local)
            if "São Luís" not in local:
                self.observar(f"Cabeçalho não exibe a cidade: '{local}'")

            # Passo 5 - Pesquisar "Kindle" e abrir a página de um produto
            self.passo(5, "Abrir produto e conferir o CEP")
            self.pesquisar(config.TERMO_ENTREGA)
            link = self.js("""
                const r = [...document.querySelectorAll("[data-component-type='s-search-result']")]
                  .find(x => !x.querySelector('.puis-sponsored-label-text'));
                const a = r && r.querySelector("a[href*='/dp/']"); return a ? a.href : null;""")
            self.driver.get(link)
            self.pausa()
            loc_produto = self.js("""
                const e = document.querySelector('#contextualIngressPtLabel_deliveryShortLine, #glowContextualIngressPt_feature_div, #contextualIngressPtLabel');
                return e ? e.innerText : '';""")
            self.verificar("65075" in loc_produto, "CEP exibido na página do produto", loc_produto)

            # Passo 6 - Verificar a informação de entrega do produto
            self.passo(6, "Conferir prazo de entrega")
            entrega = self.js("""
                const e = document.querySelector('#mir-layout-DELIVERY_BLOCK, #deliveryBlockMessage');
                return e ? e.innerText.replace(/\\s+/g,' ') : '';""")
            self.verificar("Entrega" in entrega or "entrega" in entrega, "Prazo/data de entrega exibido", entrega[:120])

            # Passo 7 - Fechar e reabrir o navegador e acessar a página inicial
            self.passo(7, "Fechar e reabrir o navegador")
            self.driver.quit()
            self.driver = criar_driver(perfil)
            self.abrir()
            self.verificar("65075" in self._texto_local(), "CEP mantido após reabrir", self._texto_local())
            self.concluir()
        finally:
            # o tearDown fecha o driver; o perfil temporário é apagado depois
            self.addCleanup(shutil.rmtree, perfil, True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
