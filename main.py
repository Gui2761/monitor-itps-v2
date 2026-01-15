import os
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Selenium e Requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests 

# --- CONFIGURAÇÕES ---
URL_BUSCA = "https://iose.se.gov.br/buscanova/#/p=1&q=ITPS" 

# DADOS DO GITHUB E EMAIL
MEU_EMAIL = os.environ["EMAIL_USER"]
MINHA_SENHA = os.environ["EMAIL_PASS"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY")

# LISTA DE QUEM VAI RECEBER
LISTA_DESTINATARIOS = [
    "anacarolina.mota@itps.se.gov.br",
    "itpsgeprocon@gmail.com",
    "geaad@itps.se.gov.br",
    "geconf@itps.se.gov.br",
    "gpresi@itps.se.gov.br",
    "gerh@itps.se.gov.br"
]

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def ja_avisei_sobre_essa_edicao(chave_unica):
    """Verifica na memória (Issues do GitHub) se já enviamos."""
    if not GITHUB_TOKEN or not REPO_NAME: return False
    
    titulo_esperado = f"LOG: {chave_unica[:60].strip()}"
    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}", 
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Busca os últimos 100 logs
    params = {"state": "all", "labels": "log-envio", "per_page": 100}
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        
        # Se for repositório novo, não deve dar erro. Mas se der, segura a onda.
        if resp.status_code != 200:
            print(f"⚠️ Erro API ({resp.status_code}).")
            return False 

        issues = resp.json()
        if not isinstance(issues, list): return False

        for issue in issues:
            if issue["title"] == titulo_esperado:
                return True # Já enviamos!
        
        return False # É novidade!
    except Exception as e: 
        print(f"⚠️ Erro conexão: {e}")
        return False

def marcar_como_enviado(chave_unica, frase_completa):
    """Cria um Issue no GitHub para servir de memória."""
    if not GITHUB_TOKEN or not REPO_NAME: return
    
    titulo = f"LOG: {chave_unica[:60].strip()}"
    url = f"https://api.github.com/repos/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}", 
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": titulo, 
        "body": f"Enviado: {frase_completa}", 
        "labels": ["log-envio"]
    }
    
    try:
        requests.post(url, headers=headers, data=json.dumps(data))
    except:
        pass 

def enviar_email(frase_encontrada, nome_edicao):
    hora_brasil = datetime.utcnow() - timedelta(hours=3)
    data_formatada = hora_brasil.strftime("%d/%m/%Y")

    assunto_resumido = nome_edicao.replace("Diário Oficial do Estado de Sergipe", "").replace("publicado em:", "").strip()
    if len(assunto_resumido) < 5: assunto_resumido = f"Edição de {data_formatada}"

    assunto = f"🔔 ITPS ENCONTRADO: {assunto_resumido}"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <div style="background-color: #004a8f; padding: 20px; text-align: center; color: #ffffff;">
            <h2 style="margin: 0;">Monitoramento ITPS</h2>
          </div>
          <div style="padding: 30px;">
            <p style="font-size: 16px; color: #333;">Olá,</p>
            <p style="font-size: 16px; color: #333;">O robô detectou menção ao ITPS em uma nova edição:</p>
            <div style="background-color: #eef6fc; border-left: 5px solid #004a8f; padding: 15px; margin: 20px 0;">
              <p style="margin: 0 0 10px; font-size: 14px; color: #555;"><strong>📅 Data:</strong> {data_formatada}</p>
              <p style="margin: 0; font-size: 15px; color: #000;"><strong>📄 Edição Detectada:</strong></p>
              <p style="margin: 5px 0 0; font-style: italic; color: #333;">"{frase_encontrada}"</p>
            </div>
            <p style="text-align: center; margin-top: 30px;">
              <a href="{URL_BUSCA}" style="background-color: #28a745; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                Visualizar no Site ➔
              </a>
            </p>
          </div>
          <div style="background-color: #eeeeee; padding: 15px; text-align: center; font-size: 12px; color: #777;">
            <p style="margin: 0;">Alerta Automático.</p>
          </div>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['Subject'] = assunto
    msg['From'] = MEU_EMAIL
    msg['To'] = ", ".join(LISTA_DESTINATARIOS)
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MEU_EMAIL, MINHA_SENHA)
            s.sendmail(MEU_EMAIL, LISTA_DESTINATARIOS, msg.as_string())
        print(f">>> E-MAIL ENVIADO! Assunto: {assunto}")
    except Exception as e:
        print(f"Erro email: {e}")

def verificar_busca():
    hora_brasil = datetime.utcnow() - timedelta(hours=3)
    hoje_str = hora_brasil.strftime("%d/%m/%Y")
    termo_data = f"publicado em: {hoje_str}" 
    
    print(f"--- Buscando por ITPS no dia: {hoje_str} ---")
    
    edicoes_processadas_agora = []
    driver = get_driver()
    try:
        driver.get(URL_BUSCA)
        print("Aguardando resultados (20s)...")
        time.sleep(20)
        
        texto_pagina = driver.find_element(by="tag name", value="body").text
        linhas = texto_pagina.split('\n')
        encontrou_algo = False
        
        for linha in linhas:
            if termo_data in linha:
                # Cria chave única (Ex: "Diário Oficial - Edição 29808")
                chave_unica = linha.split(" - Pág.")[0]

                if chave_unica in edicoes_processadas_agora: continue
                
                print(f"Analisando: {chave_unica}...")
                
                # NOVO REPOSITÓRIO = MEMÓRIA VAZIA = VAI ENVIAR A PRIMEIRA VEZ E DEPOIS LEMBRAR
                if ja_avisei_sobre_essa_edicao(chave_unica):
                    print("-> Já avisei. Ignorando.")
                    edicoes_processadas_agora.append(chave_unica)
                else:
                    print("-> NOVIDADE! Enviando alerta...")
                    enviar_email(linha, chave_unica) 
                    marcar_como_enviado(chave_unica, linha) 
                    edicoes_processadas_agora.append(chave_unica)
                    encontrou_algo = True
        
        if not encontrou_algo: print("Nenhum resultado NOVO encontrado.")

    except Exception as e: print(f"Erro Selenium: {e}")
    finally: driver.quit()

if __name__ == "__main__":
    verificar_busca()
