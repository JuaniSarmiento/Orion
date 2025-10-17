"""
Notifications Module - Email Alerts for Escalations
====================================================
Handles email notifications for critical events such as escalation to human.

This module provides async functions to send email notifications when
automated systems need human intervention, ensuring the support team
is promptly informed.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import asyncio
from functools import wraps


def async_to_sync(func):
    """
    Decorator to run blocking functions in a thread pool.
    This prevents SMTP blocking operations from blocking the async event loop.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


@async_to_sync
def _send_email_sync(
    subject: str,
    body: str,
    to_email: str,
    from_email: str,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str
) -> bool:
    """
    Synchronous email sending function (wrapped to be async).
    
    This function performs the actual SMTP connection and email sending.
    It's wrapped with async_to_sync to prevent blocking the event loop.
    
    Args:
        subject (str): Email subject line
        body (str): Email body content (plain text or HTML)
        to_email (str): Recipient email address
        from_email (str): Sender email address
        smtp_server (str): SMTP server hostname
        smtp_port (int): SMTP server port (typically 587 for TLS)
        username (str): SMTP authentication username
        password (str): SMTP authentication password
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # Attach body as plain text
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Connect to SMTP server and send email
        print(f"📧 Conectando a servidor SMTP: {smtp_server}:{smtp_port}")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Enable TLS encryption
            server.starttls()
            print(f"🔐 TLS activado, autenticando...")
            
            # Login to SMTP server
            server.login(username, password)
            print(f"✅ Autenticación exitosa")
            
            # Send email
            server.send_message(msg)
            print(f"✅ Email enviado exitosamente a {to_email}")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {str(e)}")
        print(f"   Verifica MAIL_USERNAME y MAIL_PASSWORD en .env")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado al enviar email: {str(e)}")
        return False


async def send_escalation_email(user_id: str, last_message: str, failed_attempts: int = 2) -> bool:
    """
    Send escalation notification email to support team.
    
    This async function sends an email alert when a user has exceeded the
    threshold of failed intent attempts, indicating that human intervention
    is needed. The email includes user identification and context about the
    failed interaction.
    
    Args:
        user_id (str): Unique identifier of the user requiring escalation
        last_message (str): The last message sent by the user
        failed_attempts (int): Number of consecutive failed attempts (default: 2)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    
    Environment Variables Required:
        - MAIL_SERVER: SMTP server hostname (e.g., smtp.gmail.com)
        - MAIL_PORT: SMTP server port (e.g., 587)
        - MAIL_USERNAME: SMTP authentication username
        - MAIL_PASSWORD: SMTP authentication password
        - MAIL_FROM: Sender email address
        - MAIL_TO: Recipient email address (support team)
        - MAIL_SUBJECT_PREFIX: Optional subject prefix (default: [ORION])
    
    Example:
        >>> await send_escalation_email("+5491112345678", "Quiero hablar con alguien", 2)
        True
    """
    # Load email configuration from environment variables
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', '587'))
    mail_username = os.getenv('MAIL_USERNAME', '')
    mail_password = os.getenv('MAIL_PASSWORD', '')
    mail_from = os.getenv('MAIL_FROM', mail_username)
    mail_to = os.getenv('MAIL_TO', 'soporte@ejemplo.com')
    subject_prefix = os.getenv('MAIL_SUBJECT_PREFIX', '[ORION]')
    
    # Validate configuration
    if not all([mail_username, mail_password, mail_from, mail_to]):
        print("⚠️ Configuración de email incompleta en variables de entorno")
        print(f"   MAIL_USERNAME: {'✅' if mail_username else '❌ FALTA'}")
        print(f"   MAIL_PASSWORD: {'✅' if mail_password else '❌ FALTA'}")
        print(f"   MAIL_FROM: {'✅' if mail_from else '❌ FALTA'}")
        print(f"   MAIL_TO: {'✅' if mail_to else '❌ FALTA'}")
        print(f"   Saltando envío de email...")
        return False
    
    # Build email subject
    subject = f"🚨 {subject_prefix} Escalación a Humano Requerida - Usuario: {user_id}"
    
    # Build email body with rich context
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    body = f"""
╔══════════════════════════════════════════════════════════════╗
║          🚨 ALERTA DE ESCALACIÓN A HUMANO                    ║
╚══════════════════════════════════════════════════════════════╝

Se ha detectado que un usuario requiere asistencia humana debido a 
múltiples intentos fallidos de comprensión por parte del bot.

DETALLES DEL USUARIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 ID de Usuario:        {user_id}
⚠️  Intentos Fallidos:    {failed_attempts}
💬 Último Mensaje:        "{last_message}"
🕐 Fecha/Hora:           {timestamp}

CONTEXTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
El bot no pudo comprender las últimas {failed_attempts} consultas del usuario,
lo que indica una posible frustración o necesidad de asistencia
especializada.

ACCIONES RECOMENDADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Revisar el historial completo de la conversación
2. Contactar al usuario lo antes posible
3. Identificar la necesidad no cubierta por el bot
4. Documentar el caso para mejorar el sistema NLU

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Sistema ORION - Core Service
📧 Esta es una notificación automática
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """.strip()
    
    # Log the escalation notification attempt
    print(f"\n{'='*70}")
    print(f"📧 Preparando email de escalación...")
    print(f"   Para: {mail_to}")
    print(f"   Asunto: {subject}")
    print(f"{'='*70}\n")
    
    # Send email asynchronously (blocking SMTP operations run in thread pool)
    result = await _send_email_sync(
        subject=subject,
        body=body,
        to_email=mail_to,
        from_email=mail_from,
        smtp_server=mail_server,
        smtp_port=mail_port,
        username=mail_username,
        password=mail_password
    )
    
    if result:
        print(f"\n{'='*70}")
        print(f"✅ Notificación de escalación enviada exitosamente")
        print(f"{'='*70}\n")
    else:
        print(f"\n{'='*70}")
        print(f"❌ No se pudo enviar la notificación de escalación")
        print(f"{'='*70}\n")
    
    return result
