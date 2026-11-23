# Automação dos Casos de Teste — Amazon Brasil

Automação, em **Selenium com Python** (Aula 6), dos casos de teste do documento
*Definição dos Casos de Teste - Amazon*. Ao final da execução, os resultados
são gravados automaticamente na planilha **03 - Acompanhamento Bugs - Amazon.xlsx**.

## 1. O que foi automatizado

| CT | Caso de teste | Automatizado? |
|----|---------------|---------------|
| CT_001 | Navegar por departamento pelo menu "Todos" | Sim |
| CT_002 | Filtrar por faixa de preço e avaliação | Sim |
| CT_003 | Ordenar resultados por preço | Sim |
| CT_004 | Selecionar variação de um produto (cor) | Sim |
| CT_005 | Filtrar ofertas e validar o % de desconto | Sim |
| CT_006 | Alterar o idioma do site | Sim |
| CT_007 | Validar campos do cadastro | **Não** (CAPTCHA/código de verificação) |
| CT_008 | Lista de Desejos | **Não** (exige login) |
| CT_009 | Entrega por CEP | Sim |
| CT_010 | Logout e páginas protegidas | **Não** (exige login) |

Foram automatizados só os casos que o documento marca com `Automatizado (Sim/Não) = Sim`.

## 2. Como o roteiro da Aula 6 foi aplicado

| Slide da Aula 6 | Onde aparece no projeto |
|-----------------|-------------------------|
| `pip install selenium` + driver do navegador | `requirements.txt`. No Selenium 4.6+, o *Selenium Manager* baixa o ChromeDriver sozinho, então não é preciso o `chromedriver.exe`. |
| Usar a lib `unittest` | `test_amazon.py`: classe `TestesAmazonBrasil(unittest.TestCase)` |
| `driver.get(url)` e interação com elementos | `find_element(By.ID / By.NAME / By.XPATH / By.CSS_SELECTOR, ...)` |
| Ocultar a GUI (`--headless`) | `config.HEADLESS` ou `python executar_testes.py --headless` |
| `implicitly_wait(time)` e `time.sleep(t)` | `base.py` → `criar_driver()` e `pausa()` |
| Comentar o script com os passos do CT | Cada método tem `# Passo N - ...` copiado do documento |
| `Select(...).select_by_visible_text(...)` | CT_003: `Select(...).select_by_value("price-asc-rank")` |

> **Atenção à sintaxe:** a aula usa `find_element_by_name("q")`, que foi **removido** no
> Selenium 4. O equivalente atual é `find_element(By.NAME, "q")`.

## 3. Como executar

```bash
# 1) Instale as dependências (uma vez)
pip install -r requirements.txt

# 2) Execute todos os CTs automatizados (abre o Chrome)
python executar_testes.py

# Opções
python executar_testes.py CT_003 CT_009   # só alguns casos
python executar_testes.py --headless      # sem janela (GUI oculta)
python executar_testes.py --sem-planilha  # não grava o relatório
```

Pré-requisitos: Python 3.9+ e Google Chrome instalado. A planilha
`03 - Acompanhamento Bugs - Amazon.xlsx` deve estar **na pasta acima** de `automacao_amazon/`
(ou ajuste `PLANILHA_ACOMPANHAMENTO` em `config.py`). Feche a planilha no Excel antes de rodar.

## 4. O que acontece na planilha

- **Execução de Casos de Teste**: para cada CT executado, preenche a Data, o Status
  (`Passou`, `Falhou` ou `Não foi Possível Executar`), o Responsável e a Descrição do Problema,
  com o caminho da evidência (print da tela final).
- **Log da Automação**: uma linha por passo (OK / FALHOU / ERRO / IMPEDIDO), para rastrear
  em qual passo o caso falhou.
- **Resumo**: as métricas (taxa de aprovação, cobertura, bugs por severidade) são fórmulas
  e se atualizam sozinhas.
- **Registro de Bugs**: é preenchida pelo analista. A automação mostra a falha; quem decide
  se é bug, severidade e prioridade é você (Aula 9).

## 5. Decisões técnicas (para explicar na apresentação)

1. **Verificação suave (soft assertion)**: `self.verificar(...)` registra a falha e **continua**
   o caso. Assim, se os passos 4 e 6 do CT_003 falharem, os dois aparecem no relatório. Um
   `assert` comum pararia no primeiro erro.
2. **"Não foi Possível Executar" ≠ "Falhou"**: se aparecer CAPTCHA da Amazon ou a tela
   "modo protegido do navegador" do antivírus, o caso é marcado como *impedido*. Isso não é
   defeito do sistema e não deve virar bug (evita **falso positivo**).
3. **Itens patrocinados são ignorados** nas verificações de ordenação e preço, porque anúncios
   não seguem a ordenação escolhida.
4. **CT_009, passo 7 ("fechar e reabrir o navegador")**: o teste usa um perfil próprio do Chrome
   (`--user-data-dir`), fecha o driver e abre outro com o mesmo perfil, como faria um usuário.

## 6. Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---------|----------------|-------------|
| Tela "O site está aberto no modo protegido do navegador" | Kaspersky (Navegação Segura) intercepta a Amazon | Adicione `amazon.com.br` às exceções do Kaspersky ou rode em `--headless` |
| Caso marcado "Não foi Possível Executar – CAPTCHA" | Proteção anti-robô da Amazon | Aguarde alguns minutos e rode só aquele CT |
| `NoSuchElementException` | A Amazon mudou o layout ou o ID do elemento | Inspecione o elemento no DevTools (F12) e atualize o seletor |
| `PermissionError` ao salvar a planilha | Planilha aberta no Excel | Feche o arquivo e rode de novo |

## 7. Estrutura

```
automacao_amazon/
├── config.py            # URL, dados de teste, headless, esperas, caminho da planilha
├── base.py              # driver, esperas, soft assertions, tratamento de CAPTCHA/antivírus
├── test_amazon.py       # os 7 casos automatizados (um método por CT)
├── executar_testes.py   # roda a suíte e grava a planilha
├── relatorio_excel.py   # escrita na planilha (openpyxl)
├── requirements.txt
└── evidencias/          # prints da execução
```
