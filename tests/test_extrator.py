import os
import glob

def test_excel_gerado():
    # Busca arquivos .xlsx na pasta dados
    arquivos = glob.glob("dados/*.xlsx")
    # Espera pelo menos 1 arquivo xlsx
    assert len(arquivos) > 0, "Nenhum arquivo .xlsx encontrado na pasta dados"
