# -*- coding: utf-8 -*-
"""
Configurações da automação dos casos de teste da Amazon Brasil.

Altere os valores abaixo conforme o seu ambiente. Nenhuma senha é
necessária: os casos automatizados (CT_001 a CT_006 e CT_009) não
exigem login. Os casos CT_007, CT_008 e CT_010 continuam MANUAIS,
conforme o campo "Automatizado (Sim/Não)" do documento de casos de teste.
"""

from pathlib import Path

# --- Sistema sob teste ------------------------------------------------------
URL_BASE = "https://www.amazon.com.br/"
NOME_SISTEMA = "Amazon Brasil (www.amazon.com.br)"

# --- Navegador ----------------------------------------------------------------
# True  = executa sem abrir a janela do Chrome (Aula 6: "Ocultando a GUI")
# False = abre o Chrome para você acompanhar cada passo
HEADLESS = False

# Espera implícita do Selenium (Aula 6: driver.implicitly_wait(time))
ESPERA_IMPLICITA = 10          # segundos
# Pausa curta entre passos (Aula 6: time.sleep(t)) para a página reagir
PAUSA_ENTRE_PASSOS = 2         # segundos
# Tempo máximo das esperas explícitas (WebDriverWait)
ESPERA_EXPLICITA = 15          # segundos

# --- Relatório ----------------------------------------------------------------
PASTA_PROJETO = Path(__file__).resolve().parent
PLANILHA_ACOMPANHAMENTO = PASTA_PROJETO.parent / "03 - Acompanhamento Bugs - Amazon.xlsx"
PASTA_EVIDENCIAS = PASTA_PROJETO / "evidencias"
RESPONSAVEL_EXECUCAO = "Isaac"

# --- Dados de teste (iguais aos do documento de casos de teste) ---------------
DEPARTAMENTO = "Computadores e Informática"
SUBCATEGORIA = "Notebooks"
TERMO_FILTROS = "caixa de som bluetooth"
TERMO_ORDENACAO = "mouse sem fio"
TERMO_VARIACAO = "Echo Dot 5ª geração"
COR_VARIACAO = "Branco"
URL_OFERTAS = URL_BASE + "deals"
DEPARTAMENTO_OFERTAS = "Eletrônicos e Tecnologia"   # rótulo atual do site
DESCONTO_MINIMO = 25                                  # %
CEP_INVALIDO = ("00000", "000")
CEP_LETRAS = ("abcde", "fgh")
CEP_VALIDO = ("65075", "441")                         # São Luís - MA
TERMO_ENTREGA = "Kindle"

# Casos de teste que o documento marca como "Automatizado = Não"
CASOS_MANUAIS = {
    "CT_007": "Cadastro exige verificação por código/CAPTCHA (execução manual).",
    "CT_008": "Requer sessão autenticada com conta de teste (execução manual).",
    "CT_010": "Requer sessão autenticada com conta de teste (execução manual).",
}
