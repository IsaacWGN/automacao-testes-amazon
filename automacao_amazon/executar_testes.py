# -*- coding: utf-8 -*-
"""
Executa a suíte automatizada e atualiza a planilha de acompanhamento.

Uso:
    python executar_testes.py                  # todos os CTs automatizados
    python executar_testes.py CT_003 CT_009    # apenas os CTs informados
    python executar_testes.py --headless       # sem abrir a janela do Chrome
    python executar_testes.py --sem-planilha   # só executa, não grava o relatório
"""

import argparse
import sys
import time
import unittest

import config
from relatorio_excel import (STATUS_FALHOU, STATUS_IMPEDIDO, STATUS_PASSOU,
                             gravar_resultados)
from test_amazon import TestesAmazonBrasil


class ResultadoColetado(unittest.TextTestResult):
    """Guarda o status de cada CT no formato da planilha."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registros = []

    def _registrar(self, teste, status, problema):
        self.registros.append({
            "codigo": teste.codigo_ct(),
            "status": status,
            "problema": problema,
            "passos": getattr(teste, "passos", []),
            "evidencia": getattr(teste, "evidencia", ""),
            "observacoes": getattr(teste, "observacoes", []),
        })

    def addSuccess(self, teste):
        super().addSuccess(teste)
        obs = getattr(teste, "observacoes", [])
        self._registrar(teste, STATUS_PASSOU, ("Observações: " + " | ".join(obs)) if obs else "")

    def addFailure(self, teste, err):
        super().addFailure(teste, err)
        texto = str(err[1])
        obs = getattr(teste, "observacoes", [])
        if obs:
            texto += " || Observações: " + " | ".join(obs)
        self._registrar(teste, STATUS_FALHOU, texto)

    @staticmethod
    def _marcar_ultimo_passo(teste, resultado, detalhe):
        passos = getattr(teste, "passos", [])
        if passos:
            passos[-1]["resultado"] = resultado
            passos[-1]["detalhe"] = detalhe[:300]

    def addError(self, teste, err):
        super().addError(teste, err)
        self._marcar_ultimo_passo(teste, "ERRO", f"{err[0].__name__}: {str(err[1]).splitlines()[0]}")
        self._registrar(teste, STATUS_FALHOU,
                        f"Erro de execução no passo {getattr(teste, 'passo_atual', '?')}: "
                        f"{err[0].__name__}: {str(err[1]).splitlines()[0][:300]}")

    def addSkip(self, teste, motivo):
        super().addSkip(teste, motivo)
        self._marcar_ultimo_passo(teste, "IMPEDIDO", motivo)
        self._registrar(teste, STATUS_IMPEDIDO, motivo)


def main():
    parser = argparse.ArgumentParser(description="Automação dos CTs - Amazon Brasil")
    parser.add_argument("cts", nargs="*", help="Códigos dos CTs (ex.: CT_001 CT_003)")
    parser.add_argument("--headless", action="store_true", help="Executar sem interface gráfica")
    parser.add_argument("--sem-planilha", action="store_true", help="Não gravar na planilha")
    args = parser.parse_args()

    if args.headless:
        config.HEADLESS = True

    carregador = unittest.TestLoader()
    nomes = sorted(n for n in carregador.getTestCaseNames(TestesAmazonBrasil))
    if args.cts:
        nomes = [n for n in nomes if any(ct.upper() in n.upper() for ct in args.cts)]
    suite = unittest.TestSuite(TestesAmazonBrasil(n) for n in nomes)

    print(f"Executando {len(nomes)} caso(s) automatizado(s) em {config.URL_BASE}\n")
    inicio = time.time()
    runner = unittest.TextTestRunner(verbosity=2, resultclass=ResultadoColetado)
    resultado = runner.run(suite)
    duracao = time.time() - inicio

    print("\n================ RESUMO ================")
    for r in resultado.registros:
        print(f"{r['codigo']}: {r['status']}")
        if r["problema"]:
            print(f"   {r['problema'][:400]}")
    for ct, motivo in config.CASOS_MANUAIS.items():
        print(f"{ct}: manual - {motivo}")
    print(f"Tempo total: {duracao:.0f}s")

    if not args.sem_planilha:
        gravar_resultados(config.PLANILHA_ACOMPANHAMENTO, resultado.registros,
                          config.RESPONSAVEL_EXECUCAO)
        print(f"\nPlanilha atualizada: {config.PLANILHA_ACOMPANHAMENTO}")

    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
