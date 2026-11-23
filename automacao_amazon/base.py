# -*- coding: utf-8 -*-
"""
Infraestrutura comum dos testes (Aula 6 - Selenium com Python).

- Cria o driver do Chrome (com opção headless, como no slide "Ocultando a GUI").
- Define a espera implícita (driver.implicitly_wait) e pausas (time.sleep).
- Oferece "verificações suaves" (soft assertions): o teste continua após
  uma falha de verificação e, no final, reporta TODOS os passos que falharam.
  Assim a planilha mostra exatamente quais passos do caso de teste falharam.
- Trata telas de proteção que impedem o teste (CAPTCHA da Amazon e a tela
  "modo protegido do navegador" do Kaspersky), marcando o caso como
  "Não foi Possível Executar" em vez de "Falhou".
"""

import re
import time
import unittest
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


class ExecucaoImpedida(unittest.SkipTest):
    """Algo externo ao sistema impediu a execução (CAPTCHA, antivírus, rede)."""


def criar_driver(perfil=None):
    """Cria o ChromeDriver. O Selenium 4.6+ baixa o driver sozinho (Selenium Manager)."""
    chrome_options = Options()
    if config.HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1366,900")
    chrome_options.add_argument("--lang=pt-BR")
    if perfil:
        # Perfil próprio: permite "fechar e reabrir o navegador" mantendo cookies (CT_009)
        chrome_options.add_argument(f"--user-data-dir={perfil}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(config.ESPERA_IMPLICITA)
    return driver


def preco_para_float(texto):
    """Converte 'R$ 3.988,09' -> 3988.09. Retorna None se não houver número."""
    if not texto:
        return None
    limpo = re.sub(r"[^0-9,\.]", "", texto)
    if not limpo:
        return None
    limpo = limpo.replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


class TesteAmazonBase(unittest.TestCase):
    """Classe-mãe de todos os casos de teste."""

    driver = None

    # ---------------------------------------------------------------- ciclo de vida
    def setUp(self):
        self.falhas = []          # passos que falharam (soft assertions)
        self.observacoes = []     # registros informativos (não reprovam o caso)
        self.passos = []          # log completo passo a passo
        self.driver = criar_driver()
        self.espera = WebDriverWait(self.driver, config.ESPERA_EXPLICITA)

    def tearDown(self):
        # Evidência: captura de tela do estado final de cada caso
        try:
            config.PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
            nome = f"{self.codigo_ct()}_{datetime.now():%Y%m%d_%H%M%S}.png"
            caminho = config.PASTA_EVIDENCIAS / nome
            self.driver.save_screenshot(str(caminho))
            self.evidencia = str(caminho)
        except Exception:
            self.evidencia = ""
        finally:
            self.driver.quit()

    # ---------------------------------------------------------------- utilidades
    def codigo_ct(self):
        achado = re.search(r"CT_\d{3}", self._testMethodName)
        return achado.group(0) if achado else self._testMethodName

    def pausa(self, segundos=None):
        time.sleep(config.PAUSA_ENTRE_PASSOS if segundos is None else segundos)

    def passo(self, numero, descricao):
        """Registra o início de um passo (aparece no console e no log da planilha)."""
        self.passo_atual = numero
        print(f"   [{self.codigo_ct()}] Passo {numero} - {descricao}")
        self.passos.append({"passo": numero, "acao": descricao, "resultado": "OK", "detalhe": ""})

    def verificar(self, condicao, esperado, obtido=""):
        """Soft assertion: registra a falha do passo atual e continua o teste."""
        if not condicao:
            msg = f"Passo {self.passo_atual}: esperado '{esperado}'"
            if obtido:
                msg += f" | obtido: {obtido}"
            self.falhas.append(msg)
            if self.passos:
                self.passos[-1]["resultado"] = "FALHOU"
                self.passos[-1]["detalhe"] = msg
            print(f"      X {msg}")
        return condicao

    def observar(self, texto):
        """Registra algo relevante que não reprova o caso (ex.: divergência de layout)."""
        msg = f"Passo {self.passo_atual}: {texto}"
        self.observacoes.append(msg)
        if self.passos:
            self.passos[-1]["detalhe"] = (self.passos[-1]["detalhe"] + " " + msg).strip()
        print(f"      i {msg}")

    def concluir(self):
        """Chamado no final de cada CT: reprova se algum passo falhou."""
        if self.falhas:
            self.fail(" || ".join(self.falhas))

    # ---------------------------------------------------------------- navegação
    def abrir(self, url=config.URL_BASE):
        self.driver.get(url)
        self.pausa()
        self.tratar_bloqueios()

    def tratar_bloqueios(self):
        """Detecta telas que impedem o teste e, quando possível, segue adiante."""
        titulo = (self.driver.title or "").lower()
        if "modo protegido" in titulo:
            raise ExecucaoImpedida(
                "Antivírus (Kaspersky - modo protegido do navegador) interceptou a página. "
                "Adicione amazon.com.br às exceções do 'Navegação Segura' e execute novamente."
            )
        if self.driver.find_elements(By.CSS_SELECTOR, "form[action*='validateCaptcha']"):
            raise ExecucaoImpedida("A Amazon exibiu um CAPTCHA (proteção anti-robô).")
        # Tela intermediária "Clique no botão abaixo para continuar comprando"
        botoes = self.driver.find_elements(
            By.XPATH, "//button[contains(normalize-space(), 'Continuar comprando')]")
        if botoes:
            botoes[0].click()
            self.pausa()

    def pesquisar(self, termo):
        caixa = self.espera.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        caixa.clear()
        caixa.send_keys(termo)
        self.driver.find_element(By.ID, "nav-search-submit-button").click()
        self.pausa()
        self.tratar_bloqueios()

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)

    # ---------------------------------------------------------------- resultados de busca
    def resultados(self, incluir_patrocinados=False):
        itens = self.driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
        if incluir_patrocinados:
            return itens
        return [i for i in itens
                if not i.find_elements(By.CSS_SELECTOR, ".puis-sponsored-label-text")]

    def precos_dos_resultados(self, quantidade=10):
        """Preço em destaque de cada resultado (ignora itens sem preço e patrocinados)."""
        dados = self.js("""
            return [...document.querySelectorAll("[data-component-type='s-search-result']")]
              .filter(r => !r.querySelector('.puis-sponsored-label-text'))
              .map(r => {
                 const p = r.querySelector('.a-price:not(.a-text-price) .a-offscreen');
                 const t = r.querySelector('h2');
                 return {asin: r.dataset.asin, preco: p ? p.textContent : null,
                         titulo: t ? t.innerText.slice(0, 60) : ''};
              });""")
        lista = []
        for item in dados:
            valor = preco_para_float(item["preco"])
            if valor is not None:
                lista.append({"asin": item["asin"], "preco": valor, "titulo": item["titulo"]})
        return lista[:quantidade]

    def existe(self, by, seletor):
        self.driver.implicitly_wait(1)
        try:
            return len(self.driver.find_elements(by, seletor)) > 0
        finally:
            self.driver.implicitly_wait(config.ESPERA_IMPLICITA)

    def esperar_visivel(self, by, seletor, tempo=None):
        try:
            return WebDriverWait(self.driver, tempo or config.ESPERA_EXPLICITA).until(
                EC.visibility_of_element_located((by, seletor)))
        except TimeoutException:
            return None


__all__ = ["TesteAmazonBase", "ExecucaoImpedida", "criar_driver", "preco_para_float",
           "By", "EC", "WebDriverWait", "NoSuchElementException", "TimeoutException"]
