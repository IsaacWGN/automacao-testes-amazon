# Automação de Testes — Amazon Brasil

Automação de casos de teste funcionais do site [amazon.com.br](https://www.amazon.com.br), feita com **Python + Selenium WebDriver + unittest**. Ao final de cada execução, o resultado é gravado automaticamente na planilha de acompanhamento de bugs.

Trabalho da disciplina **Teste e Qualidade de Software** — curso de Análise e Desenvolvimento de Sistemas (ADS).
Autor: **Isaac Nascimento**

---

## Resumo

| Item | Detalhe |
| --- | --- |
| Casos de teste definidos | 10 (CT_001 a CT_010) |
| Casos automatizados | 7 (CT_001 a CT_006 e CT_009) — os que o documento marca como "Automatizado = Sim" |
| Casos manuais | 3 (CT_007, CT_008 e CT_010) — dependem de login, CAPTCHA ou código de verificação |
| Execução | 23/11/2026 — 5 passaram, 2 falharam, 3 não foram executados |
| Bugs registrados | 6 (BUG-001 a BUG-006) |

## Estrutura do repositório

```
automacao-testes-amazon/
├── automacao_amazon/          # código da automação
│   ├── config.py              # URL, dados de teste, tempos de espera, modo headless
│   ├── base.py                # classe-mãe: driver do Chrome, esperas, verificações, prints
│   ├── test_amazon.py         # os 7 casos automatizados (um método por CT)
│   ├── executar_testes.py     # ponto de entrada: roda a suíte e chama o relatório
│   ├── relatorio_excel.py     # grava os resultados na planilha (openpyxl)
│   └── requirements.txt       # selenium e openpyxl
├── 1 - Instalar dependencias.bat
├── 2 - Ensaio completo (7 CTs).bat
├── 3 - Demonstracao 5 min (CT_003).bat
├── 3 - Demonstracao em sala (CT_001 e CT_003).bat
├── 4 - Restaurar planilha.bat
├── 03 - Acompanhamento Bugs - Amazon.xlsx          # planilha com os resultados
├── 03 - Acompanhamento Bugs - Amazon - RESERVA.xlsx
├── evidencias/
│   ├── execucao-assistida/    # prints dos bugs encontrados
│   └── execucao-automatizada/ # prints gerados pela automação (um por CT)
└── docs/
    ├── Definicao dos Casos de Teste - Amazon.pdf
    ├── Manual da automacao de testes - Amazon Brasil.pdf
    └── Manual da automacao de testes - Amazon Brasil.docx
```

## Como executar

**Pré-requisitos:** Windows, Python 3.9 ou superior (com "Add python.exe to PATH" marcado na instalação) e Google Chrome.

1. Baixe o repositório (**Code > Download ZIP**) e extraia a pasta.
2. Dê dois cliques em `1 - Instalar dependencias.bat`.
3. Feche a planilha no Excel e dê dois cliques em um dos atalhos:
   - `2 - Ensaio completo (7 CTs).bat` — roda os 7 casos automatizados;
   - `3 - Demonstracao 5 min (CT_003).bat` — roda só o CT_003.
4. Ao final, confira o `RESUMO` no terminal e a planilha `03 - Acompanhamento Bugs - Amazon.xlsx`.
5. Para voltar a planilha ao estado original, use `4 - Restaurar planilha.bat`.

Pela linha de comando:

```bash
cd automacao_amazon
pip install -r requirements.txt
python executar_testes.py                 # todos os casos automatizados
python executar_testes.py CT_003 CT_009   # casos escolhidos
python executar_testes.py --headless      # sem abrir a janela do Chrome
python executar_testes.py --sem-planilha  # não grava na planilha
```

O ChromeDriver é baixado automaticamente pelo Selenium Manager (Selenium 4.6+).

## Como a planilha é alimentada

1. O `.bat` chama `python executar_testes.py`.
2. O `unittest` executa os casos de `test_amazon.py` no Chrome.
3. A classe `ResultadoColetado` traduz o resultado de cada caso em **Passou**, **Falhou** ou **Não foi Possível Executar** (CAPTCHA ou antivírus, que não são defeitos do sistema).
4. A função `gravar_resultados()` (`relatorio_excel.py`) grava na aba **Execução de Casos de Teste** a data, o status, o responsável, a descrição do problema e o caminho do print, e acrescenta uma linha por passo na aba **Log da Automação**.
5. A aba **Resumo** recalcula as métricas por fórmula.

## Resultados da execução (23/11/2026)

| CT | Caso de teste | Automatizado | Status |
| --- | --- | --- | --- |
| CT_001 | Navegar por departamento pelo menu "Todos" | Sim | Passou |
| CT_002 | Filtrar por faixa de preço e avaliação | Sim | Passou |
| CT_003 | Ordenar resultados por preço | Sim | **Falhou** |
| CT_004 | Selecionar variação de um produto (cor) | Sim | Passou |
| CT_005 | Filtrar ofertas e validar o % de desconto | Sim | Passou |
| CT_006 | Alterar o idioma do site | Sim | **Falhou** |
| CT_007 | Validar campos do cadastro | Não | Não foi Possível Executar |
| CT_008 | Lista de Desejos | Não | Não foi Possível Executar |
| CT_009 | Consultar entrega por CEP | Sim | Passou |
| CT_010 | Logout e páginas protegidas | Não | Não foi Possível Executar |

## Bugs registrados

| ID | Título | Severidade | Prioridade |
| --- | --- | --- | --- |
| BUG-001 | CT_003 - Busca - Ordenar por preço - Ordem "menor para o maior" exibe R$ 8,90 depois de R$ 9,02 e R$ 9,57 | Média | Média |
| BUG-002 | CT_003 - Busca - Ordenar por preço - Ordem "maior para o menor" exibe preços fora de ordem (R$ 3.988,09 → R$ 5.945,17) | Média | Alta |
| BUG-003 | CT_006 - Preferências - Alterar idioma - Seletor de idioma ausente e página de preferências sem opções | Média | Média |
| BUG-004 | CT_004 - Página do produto - Selecionar variação - Título da aba não acompanha a cor selecionada | Baixa | Baixa |
| BUG-005 | CT_009 - Localização - Informar CEP - Cabeçalho exibe CEP sem cidade e sem máscara; campo aceita letras | Baixa | Baixa |
| BUG-006 | CT_003 - Busca - Pesquisar produto - Busca por "mouse sem fio" retorna mouses com fio | Baixa | Média |

O registro completo (passos para reproduzir, resultado esperado e atual, evidência, hipótese de causa, sugestão de correção e testes de regressão) está na aba **Registro de Bugs** da planilha.

## Decisões técnicas

- **Verificação suave (soft assertion):** `verificar()` registra a falha e continua o caso, para que o relatório mostre todos os passos com problema, e não só o primeiro.
- **"Falhou" ≠ "Não foi Possível Executar":** CAPTCHA da Amazon ou bloqueio do antivírus marcam o caso como impedido, evitando falso positivo.
- **Itens patrocinados ignorados** nas verificações de ordenação e preço, porque anúncios não seguem a ordenação escolhida.
- **Dados de teste separados do código** em `config.py`.

## Observações

- Os testes rodam no site público, em produção, e apenas navegam como um cliente comum: sem login, sem compra, sem cadastro e sem testes de carga ou de segurança.
- A Amazon muda o layout com frequência. Se um seletor deixar de existir, o caso cai em erro de execução, e o seletor precisa ser atualizado em `test_amazon.py`.
