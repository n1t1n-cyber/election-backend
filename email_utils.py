import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

async def send_email(to_email: str, subject: str, html_body: str):
    """Send an HTML email using SMTP with explicit STARTTLS."""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html"))

    # Initialize the client here so the variable exists for the whole function
    smtp = aiosmtplib.SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        use_tls=True
    )

    try:
        await smtp.connect()  # Upgrades the connection to secure
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        print(f"✅ Email successfully sent to {to_email}")
    except Exception as e:
        print(f"❌ SMTP Error occurred: {e}")
        raise e 
    finally:
        # This ensures the connection closes even if it fails
        try:
            await smtp.quit()
        except:
            pass

async def send_verification_email(to_email: str, name: str, token: str):
    """Send email verification link."""
    verify_url = f"{settings.BASE_URL}/auth/verify-email?token={token}"
    subject = f"✅ Verify Your Email - {settings.APP_NAME}"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
        <div style="background: #1a1a2e; padding: 30px; border-radius: 10px; text-align: center;">
            <h1 style="color: #e94560;">🗳️ {settings.APP_NAME}</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
            <h2>Hello, {name}! 👋</h2>
            <p>Thank you for registering. Please verify your email address to activate your account.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}"
                   style="background: #e94560; color: white; padding: 14px 30px;
                          border-radius: 6px; text-decoration: none; font-size: 16px;">
                    ✅ Verify My Email
                </a>
            </div>
            <p style="color: #888; font-size: 13px;">
                This link expires in 24 hours. If you didn't register, ignore this email.
            </p>
            <p style="color: #aaa; font-size: 12px;">Or copy this link:<br>{verify_url}</p>
        </div>
    </body>
    </html>
    """
    await send_email(to_email, subject, html_body)


async def send_welcome_email(to_email: str, name: str):
    """Send welcome email after verification."""
    subject = f"🎉 Welcome to {settings.APP_NAME}!"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
        <div style="background: #1a1a2e; padding: 30px; border-radius: 10px; text-align: center;">
            <h1 style="color: #e94560;">🗳️ {settings.APP_NAME}</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <h2>Welcome aboard, {name}! 🎉</h2>
            <p>Your email has been verified. You can now:</p>
            <ul>
                <li>✅ Browse active elections</li>
                <li>✅ Cast your vote securely</li>
                <li>✅ View live election results</li>
            </ul>
            <p>Visit <a href="{settings.BASE_URL}">{settings.BASE_URL}</a> to get started.</p>
        </div>
    </body>
    </html>
    """
    await send_email(to_email, subject, html_body)
