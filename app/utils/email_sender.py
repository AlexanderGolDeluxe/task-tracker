from email.mime.text import MIMEText
from smtplib import SMTP
from ssl import create_default_context

from fastapi import BackgroundTasks
from loguru import logger

from app.config import MAIL_HOST, MAIL_PASSWORD, MAIL_PORT, MAIL_USERNAME
from app.core.schemas import TaskSchema, UserSchema


@logger.catch(reraise=True)
def notify_about_change_task_status(
        updated_task: TaskSchema,
        user_changer: UserSchema,
        background_tasks: BackgroundTasks
    ):
    """
    Generates mail text about change task status and
    creates background task to send it
    """
    mail_text = (
        f"<h1>Hello, {updated_task.responsible_person.login}</h1>"
        f"<h3>For task «<i>{updated_task.title}</i>» "
        f"status was changed to «<i>{updated_task.status.name}</i>»</h3>"
    )
    background_tasks.add_task(
        send_mail,
        mail_text=mail_text,
        mail_from=user_changer.email,
        mail_to=updated_task.responsible_person.email,
        mail_subj=f"Task «{updated_task.title}» status has been changed")


@logger.catch()
def send_mail(
        mail_text: str, mail_from: str, mail_to: str, mail_subj: str
    ):
    """
    Connects to SMTP server and
    sends message through it to specified email
    """
    message = MIMEText(mail_text, "html")
    message["From"] = mail_from
    message["To"] = mail_to
    message["Subject"] = mail_subj

    if all((MAIL_HOST, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD)):
        with SMTP(MAIL_HOST, MAIL_PORT) as mail_server:
            mail_server.ehlo()
            mail_server.starttls(context=create_default_context())
            mail_server.ehlo()
            mail_server.login(MAIL_USERNAME, MAIL_PASSWORD)
            mail_server.send_message(message)
            mail_server.quit()

        logger.info(f"Mail sended to {mail_to} successfully!")
