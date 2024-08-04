from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(user_email, course_name):
    subject = 'Подтверждение покупки курса'
    message = f'Вы успешно купили курс: {course_name}. Спасибо за вашу покупку!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)
