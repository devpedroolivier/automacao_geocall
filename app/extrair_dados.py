import json
import time
import os
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Carregar config.json
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)
site_config = config["site"]

# Diretório para downloads
download_dir = "C:\\Users\\Pedri\\automacap_geocall\\dados"

# Configuração do Chrome
options = Options()
options.add_argument("--start-maximized")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
options.add_experimental_option("prefs", prefs)

service = Service()
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(site_config["url"])
    print("[INFO] Site carregado.")
    wait = WebDriverWait(driver, 20)

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

    manobra_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="TBB_tbm2"]/div[8]')))
    manobra_btn.click()
    print("[INFO] Clicou em manobra.")
    driver.save_screenshot("pos_manobra.png")
    time.sleep(3)

    # Checkbox
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
    print("[INFO] Checkbox 'Manobra Finalizada' clicado.")
    driver.save_screenshot("pos_checkbox.png")

    # Preencher datas
    driver.execute_script('document.querySelector("input[name=\'_InXSVIAMANVALVECLOSINGFROM_D_VAL\']").value = "07/07/2025";')
    driver.execute_script('document.querySelector("input[name=\'_InXSVIAMANVALVECLOSINGTO_D_VAL\']").value = "08/07/2025";')
    print("[INFO] Datas preenchidas.")
    driver.save_screenshot("pos_datas.png")

    # Buscar
    buscar_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(@onclick, "SearchEntity#")]')))
    driver.execute_script("arguments[0].click();", buscar_btn)
    print("[INFO] Clicou no botão Buscar.")
    driver.save_screenshot("pos_busca.png")
    time.sleep(5)

    # Menu três listras
    tres_listras = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img.icon_menu[alt="Ações"]')))
    driver.execute_script("arguments[0].click();", tres_listras)
    print("[INFO] Clicou nas três listras (menu Ações).")
    driver.save_screenshot("pos_menu_acoes.png")
    time.sleep(2)

    # Relatório
    relatorio_item = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(),"Relatório de Manobra")]')))
    driver.execute_script("arguments[0].click();", relatorio_item)
    print("[INFO] Clicou na opção Relatório de Manobra.")
    driver.save_screenshot("pos_relatorio.png")

    # Espera flexível pelo download do .xls
    print("[INFO] Aguardando download do arquivo Excel (.xls)...")
    timeout = 180
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
            raise Exception("[ERRO] Timeout esperando download do Excel.")
        time.sleep(2)

    # Converter para .xlsx e renomear
    xls_path = os.path.join(download_dir, xls_file)
    novo_nome = f"Manobra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    novo_path = os.path.join(download_dir, novo_nome)

    df = pd.read_excel(xls_path)
    df.to_excel(novo_path, index=False)
    os.remove(xls_path)
    print(f"[INFO] Arquivo convertido para {novo_nome} e original .xls removido.")

except Exception as e:
    print(f"[FALHA] {e}")
    driver.save_screenshot("falha_geral.png")
finally:
    driver.quit()
    print("[INFO] Navegador fechado.")
