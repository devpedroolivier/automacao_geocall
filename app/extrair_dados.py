import json
import time
import os
import shutil
import random
from datetime import datetime, timedelta
import pandas as pd
import pytz
import glob
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

tz = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(tz)
inicio_ano = datetime(hoje.year, 1, 1, tzinfo=tz)

# 🔥 Limpar cache antigo (opcional, pois perfil é randômico)
try:
    shutil.rmtree("/tmp/chrome_profile")
    print("[INFO] Perfil Chrome anterior removido.")
except FileNotFoundError:
    pass

# Diretório de downloads
download_dir = "/app/dados"

# Preparar perfil aleatório
profile_path = f"/tmp/chrome_profile_{random.randint(1, 100000)}"

# Config Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(f"--user-data-dir={profile_path}")
options.add_argument("--start-maximized")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_settings.popups": 0,
    "profile.default_content_setting_values.automatic_downloads": 1
}
options.add_experimental_option("prefs", prefs)

# Carregar config
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)
site_config = config["site"]

service = Service()
driver = webdriver.Chrome(service=service, options=options)


def limpar_pasta(caminho_pasta, extensao):
    """
    Remove todos os arquivos com a extensão especificada de uma pasta.
    
    :param caminho_pasta: Caminho da pasta que será limpa
    :param extensao: Extensão dos arquivos a serem deletados (ex: 'xlsx', 'png')
    """
    padrao = os.path.join(caminho_pasta, f'*.{extensao}')
    arquivos = glob.glob(padrao)
    
    for arquivo in arquivos:
        try:
            os.remove(arquivo)
            print(f'🗑️ Arquivo removido: {arquivo}')
        except Exception as e:
            print(f'❌ Erro ao remover {arquivo}: {e}')


def gerar_periodos(data_inicio, data_fim, dias=5):
    periodos = []
    atual = data_inicio
    while atual <= data_fim:
        prox = atual + timedelta(days=dias-1)
        if prox > data_fim:
            prox = data_fim
        periodos.append((atual.strftime("%d/%m/%Y"), prox.strftime("%d/%m/%Y")))
        atual = prox + timedelta(days=1)
    return periodos

try:
    driver.get(site_config["url"])
    print("[INFO] Site carregado.")
    wait = WebDriverWait(driver, 30)

    iframe = wait.until(EC.presence_of_element_located((By.NAME, "mainFrame")))
    driver.switch_to.frame(iframe)
    print("[INFO] Entrou no iframe mainFrame")

    usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="USER"]')))
    senha_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="INPUTPASS"]')))
    usuario_input.clear()
    usuario_input.send_keys(site_config["usuario"])
    senha_input.clear()
    senha_input.send_keys(site_config["senha"])
    senha_input.send_keys(Keys.RETURN)
    print("[INFO] Login realizado com sucesso.")
    driver.save_screenshot("pos_login.png")
    time.sleep(3)

    periodos = gerar_periodos(inicio_ano, hoje, dias=5)
    max_retries = 3

    for idx, (data_de, data_ate) in enumerate(periodos, start=1):
        print(f"[INFO] 🔄 Buscando dados de {data_de} até {data_ate} (janela {idx}/{len(periodos)})")
        retries = 0
        while retries < max_retries:
            try:
                manobra_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="TBB_tbm2"]/div[8]')))
                manobra_btn.click()
                time.sleep(2)

                checkbox = wait.until(EC.presence_of_element_located((By.XPATH,
                    '/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/div[1]/div[2]/div/form/table/tbody/tr[12]/td[2]/div/div')))
                driver.execute_script("""
                    var evt = new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    arguments[0].dispatchEvent(evt);
                """, checkbox)
                time.sleep(1)

                driver.execute_script(f'document.querySelector("input[name=\'_InXSVIAMANVALVECLOSINGFROM_D_VAL\']").value = "{data_de}";')
                driver.execute_script(f'document.querySelector("input[name=\'_InXSVIAMANVALVECLOSINGTO_D_VAL\']").value = "{data_ate}";')
                driver.save_screenshot(f"./images/datas_{idx}.png")

                buscar_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(@onclick, "SearchEntity#")]')))
                driver.execute_script("arguments[0].click();", buscar_btn)
                time.sleep(5)

                tres_listras = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img.icon_menu[alt="Ações"]')))
                driver.execute_script("arguments[0].click();", tres_listras)
                time.sleep(1)

                relatorio_item = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(),"Relatório de Manobra")]')))
                driver.execute_script("arguments[0].click();", relatorio_item)

                print("[INFO] Aguardando download do arquivo Excel (.xls)...")
                timeout = 900
                start_time = time.time()
                xls_file = None

                while True:
                    arquivos = os.listdir(download_dir)
                    xls_files = [f for f in arquivos if f.startswith("ExcelManobra_") and f.endswith(".xls")]
                    if xls_files:
                        xls_file = xls_files[0]
                        print(f"[INFO] Arquivo gerado: {xls_file}")
                        break
                    if time.time() - start_time > timeout:
                        raise Exception(f"Timeout esperando download do Excel para o período {data_de} - {data_ate}")
                    time.sleep(2)

                xls_path = os.path.join(download_dir, xls_file)
                novo_nome = f"Manobra_{datetime.now(tz).strftime('%Y%m%d_%H%M%S')}_{idx}.xlsx"
                novo_path = os.path.join(download_dir, novo_nome)

                try:
                    df = pd.read_excel(xls_path, engine='xlrd')
                except Exception as e:
                    raise Exception(f"[ERRO] Falha ao ler o XLS {xls_path}: {e}")

                df.to_excel(novo_path, index=False)
                os.remove(xls_path)
                print(f"[INFO] ✅ Arquivo convertido para {novo_nome} e original .xls removido.")

                print(f"[INFO] Iniciando importação do arquivo {novo_path}...")
                subprocess.run(["python", "-m", "app.import_excel", novo_path], check=True)
                print(f"[INFO] Importação do {novo_nome} concluída.")
                break  # tudo certo, sai do while
            except Exception as e:
                retries += 1
                print(f"[WARN] Tentativa {retries}/{max_retries} falhou para {data_de}-{data_ate}: {e}")
                if retries >= max_retries:
                    raise Exception(f"[ERRO] Falhou {max_retries} vezes para {data_de} - {data_ate}. Abortando.")
                print("[INFO] Re-tentando operação...")
                time.sleep(5)

except Exception as e:
    print(f"[FALHA] {e}")
    driver.save_screenshot("falha_geral.png")
finally:
    driver.quit()
    print("[INFO] Navegador fechado.")
