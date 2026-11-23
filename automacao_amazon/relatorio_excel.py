# -*- coding: utf-8 -*-
"""
Atualiza a planilha "03 - Acompanhamento Bugs" com o resultado da automação.

Aba "Execução de Casos de Teste": preenche Data de Execução, Status da Execução,
Responsável e Descrição do Problema de cada CT executado.
Aba "Log da Automação": acrescenta uma linha por passo executado (rastreabilidade).
"""

from datetime import datetime

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ABA_EXECUCAO = "Execução de Casos de Teste"
ABA_LOG = "Log da Automação"

STATUS_PASSOU = "Passou"
STATUS_FALHOU = "Falhou"
STATUS_IMPEDIDO = "Não foi Possível Executar"

_borda = Border(*(Side(style="thin", color="FFB7B7B7"),) * 4)
_fonte = Font(name="Arial", size=10)
_quebra = Alignment(wrap_text=True, vertical="top")


def _linha_do_ct(aba, codigo):
    for linha in range(4, aba.max_row + 1):
        if str(aba.cell(linha, 2).value or "").strip() == codigo:
            return linha
    return None


def _aba_log(wb):
    if ABA_LOG in wb.sheetnames:
        return wb[ABA_LOG]
    aba = wb.create_sheet(ABA_LOG)
    cab = ["Data/Hora", "Caso de Teste", "Passo", "Ação", "Resultado", "Detalhe", "Evidência"]
    for col, titulo in enumerate(cab, start=1):
        c = aba.cell(1, col, titulo)
        c.font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
        c.fill = PatternFill("solid", fgColor="FF1E5E6B")
        c.border = _borda
        c.alignment = _quebra
    for col, larg in zip("ABCDEFG", (17, 13, 7, 42, 11, 80, 45)):
        aba.column_dimensions[col].width = larg
    aba.freeze_panes = "A2"
    return aba


def gravar_resultados(caminho_planilha, resultados, responsavel):
    """
    resultados: lista de dicts com as chaves
      codigo, status, problema, passos (lista de dicts), evidencia
    """
    wb = load_workbook(caminho_planilha)
    aba = wb[ABA_EXECUCAO]
    log = _aba_log(wb)
    agora = datetime.now()

    for r in resultados:
        linha = _linha_do_ct(aba, r["codigo"])
        if linha is None:
            print(f"   ! {r['codigo']} não encontrado na planilha - linha ignorada")
            continue
        aba.cell(linha, 5).value = agora.date()
        aba.cell(linha, 5).number_format = "DD/MM/YYYY"
        aba.cell(linha, 6).value = r["status"]
        aba.cell(linha, 7).value = responsavel
        texto = r["problema"] or "Nenhum problema encontrado na execução automatizada."
        if r.get("evidencia"):
            texto += f"\nEvidência: {r['evidencia']}"
        aba.cell(linha, 8).value = texto

        for p in r.get("passos", []):
            valores = [agora.strftime("%d/%m/%Y %H:%M"), r["codigo"], p["passo"], p["acao"],
                       p["resultado"], p["detalhe"], r.get("evidencia", "")]
            log.append(valores)
            for col in range(1, 8):
                c = log.cell(log.max_row, col)
                c.font, c.border, c.alignment = _fonte, _borda, _quebra
            if p["resultado"] == "FALHOU":
                log.cell(log.max_row, 5).fill = PatternFill("solid", fgColor="FFF4CCCC")

    wb.save(caminho_planilha)
