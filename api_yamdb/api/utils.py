from django.core import mail
from api_yamdb.settings import EMAIL_HOST_USER


def send_confirmation_code(to_email, confirmation_code, url):
    subject = 'Регистрация на YaMDB.'
    message = (
        'Привет! Это администрация YaMDB!\n'
        'Спасибо за регистрацию на нашем сайте!\n'
        'Аутентификация на сайте происходит с помощью JWT-токена.\n'
        'Для получения токена отправьте запрос на '
        'http://{}/api/v1/auth/token/ '
        'с данными email и confirmation_code.\n'
        'Ваш confirmation_code: {}. '
        'Никому не сообщайте этот код!'
    ).format(url, confirmation_code)
    mail.send_mail(
        subject=subject,
        message=message,
        from_email=EMAIL_HOST_USER,
        recipient_list=(to_email,),
    )
