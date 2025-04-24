import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import EMAIL_REMETENTE, SENHA_APP, EMAIL_DESTINO

def enviar_email_novo_pagamento(ano, categoria, mes, valor, pago):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = "📬 Novo pagamento adicionado"

    corpo = f"""
    Um novo pagamento foi adicionado:

    🗓 Ano: {ano}
    📂 Categoria: {categoria}
    📅 Mês: {mes}
    💰 Valor: R$ {valor:.2f}
    ✅ Pago? {"Sim" if pago else "Não"}
    """

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, SENHA_APP)
            servidor.send_message(msg)
            print("Email enviado com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
