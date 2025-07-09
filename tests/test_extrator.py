import os
import glob
import pytest

@pytest.fixture
def cria_pasta_dados():
    if not os.path.exists("dados"):
        os.makedirs("dados")
    yield
    # Aqui poderia limpar a pasta se quisesse

def test_excel_simulado(cria_pasta_dados):
    # Simula a geração de um arquivo xlsx para testar o pipeline
    fake_file = "dados/test_fake.xlsx"
    with open(fake_file, "w") as f:
        f.write("Simulando conteúdo Excel")
    assert os.path.exists(fake_file)
