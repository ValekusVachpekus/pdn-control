import os
import random
import resend
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Настраиваем API-ключ
resend.api_key = os.getenv("RESEND_API_KEY")

def generate_otp() -> str:
    """Генерирует случайный 6-значный цифровой код безопасности."""
    return str(random.randint(100000, 900000))

def send_verification_email(email: str, code: str) -> dict:
    """
    Отправляет OTP-код на указанный email через сервис Resend.
    """
    try:
        params = {
            # Если домен еще не подтвержден в панели Resend, используйте этот тестовый адрес:
            "from": "Auth <onboarding@resend.dev>",
            "to": [email],
            "subject": "Код подтверждения регистрации",
            "html": f"""
                <div style="font-family: sans-serif; padding: 20px; max-width: 500px; border: 1px solid #eee; border-radius: 8px;">
                    <h2 style="color: #333;">Добро пожаловать!</h2>
                    <p style="color: #555;">Используйте этот одноразовый код для подтверждения регистрации в сервисе проверки конфиденциальности сайтов:</p>
                    <div style="font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #4A90E2; margin: 25px 0; text-align: center; background-color: #f9f9f9; padding: 10px; border-radius: 4px;">
                        {code}
                    </div>
                    <p style="font-size: 12px; color: #999;">Код действителен в течение 10 минут. Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>
                </div>
            """
        }

        # Отправка через SDK Resend
        email_response = resend.Emails.send(params)
        return {"success": True, "data": email_response}

    except Exception as e:
        print(f"Ошибка при отправке письма через Resend: {e}")
        return {"success": False, "error": str(e)}