from django.core.mail import EmailMessage
from django.conf import settings

print("📧 Configurações atuais:")
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"TLS: {settings.EMAIL_USE_TLS}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"Password definido: {'Sim' if settings.EMAIL_HOST_PASSWORD else 'Não'}")
print(f"From: {settings.DEFAULT_FROM_EMAIL}")
print()

print("🚀 Tentando enviar email...")

try:
    email = EmailMessage(
        subject='Teste Sistema RFID - Detalhado',
        body='Se você recebeu este email, FUNCIONOU! 🎉',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['teksauloazevedo@gmail.com'],  # ⬅️ TROQUE AQUI
    )
    
    resultado = email.send()
    
    if resultado == 1:
        print("✅ Email enviado com SUCESSO!")
        print("📬 Verifique:")
        print("   1. Caixa de entrada")
        print("   2. Caixa de SPAM")
        print("   3. Pode levar alguns minutos")
    else:
        print("❌ Falha silenciosa")
        
except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")