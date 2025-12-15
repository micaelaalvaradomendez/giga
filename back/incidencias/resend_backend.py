"""
Backend de email personalizado para Django usando la API de Resend.
Reemplaza el backend SMTP para evitar el bloqueo de puertos SMTP en Railway.
"""
import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address


class ResendEmailBackend(BaseEmailBackend):
    """
    Backend de email que usa la API de Resend en lugar de SMTP.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        # Configurar API key de Resend
        resend.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        """
        Envía uno o más objetos EmailMessage y retorna el número de mensajes
        enviados exitosamente.
        """
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                # Registrar el error si es necesario
                print(f"Error enviando email via Resend: {str(e)}")

        return num_sent

    def _send(self, message):
        """
        Envía un único EmailMessage usando la API de Resend.
        """
        if not message.recipients():
            return False

        # Extraer email del remitente
        from_email = sanitize_address(message.from_email, message.encoding)
        
        # Extraer emails de los destinatarios
        recipients = [sanitize_address(addr, message.encoding) for addr in message.recipients()]

        # Preparar parámetros del email
        params = {
            "from": from_email,
            "to": recipients,
            "subject": message.subject,
        }

        # Manejar contenido HTML desde alternatives (EmailMultiAlternatives)
        html_content = None
        if hasattr(message, 'alternatives') and message.alternatives:
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_content = content
                    break
        
        # Agregar cuerpo (preferir HTML si está disponible, sino texto plano)
        if html_content:
            params["html"] = html_content
            params["text"] = message.body  # Incluir texto plano como respaldo
        elif message.content_subtype == 'html':
            params["html"] = message.body
        else:
            params["text"] = message.body

        # Agregar CC si está presente
        if message.cc:
            params["cc"] = [sanitize_address(addr, message.encoding) for addr in message.cc]

        # Agregar BCC si está presente
        if message.bcc:
            params["bcc"] = [sanitize_address(addr, message.encoding) for addr in message.bcc]

        # Agregar reply_to si está presente
        if message.reply_to:
            params["reply_to"] = [sanitize_address(addr, message.encoding) for addr in message.reply_to]

        # Enviar email via Resend
        try:
            response = resend.Emails.send(params)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            print(f"Error en API de Resend: {str(e)}")
            return False
