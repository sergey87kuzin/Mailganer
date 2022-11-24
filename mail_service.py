import re
import os
import sys
import smtplib
import argparse
from celery import Celery
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from source.global_enums import Texts
from source.mail import HTML_TEMPLATE
from dotenv import load_dotenv

app = Celery('celery_tasks', broker=os.getenv('BROKER'))


def send_single_message(sender, session, name, surname, email):
    ''' sending message to single recipient '''
    message = MIMEMultipart('alternative')
    message['Subject'] = Texts.HEADER.value
    message['From'] = sender
    check_mail(email)
    message['To'] = email
    message['Disposition-Notification-To'] = sender
    message['X-Confirm-Reading-To'] = sender

    text = Texts.BODY.value.format(
        name=name, surname=surname
    )
    part1 = MIMEText(text, 'plain')
    html = HTML_TEMPLATE.format(name=name, surname=surname)
    part2 = MIMEText(html, 'html')

    message.attach(part1)
    message.attach(part2)

    result = session.sendmail(
        sender, email, message.as_string(),
        rcpt_options=['NOTIFY=SUCCESS,DELAY,FAILURE']
    )
    if result:
        print('message was not send to {result}'.format(result=email))


@app.task
def mailing_list():
    ''' getting recipients list and sending mails '''
    load_dotenv()
    sender_address = os.getenv('SENDER_MAIL')
    sender_password = os.getenv('SENDER_PASS')
    session = smtplib.SMTP(os.getenv('HOST'), os.getenv('PORT'))
    try:
        session.ehlo()
        session.starttls()
        session.login(sender_address, sender_password)
    except Exception:
        print('can not login')
    try:
        with open(sys.argv[1], 'r') as f:
            clients = [list(line.split()) for line in f.readlines()]
            for client in clients:
                send_single_message(sender_address, session, *client)
    except Exception as e:
        print('wrong input')
        print(str(e))
    session.quit()


def check_mail(mail):
    regexp = '(@\w+\.\w+)'
    print(re.findall(regexp, mail))
    if len(re.findall(regexp, mail)) == 0:
        raise ValueError('wrong mail {email}'.format(email=mail))


def main():
    ''' service call information '''
    parser = argparse.ArgumentParser(
                prog='mail_service',
                description=Texts.FULL_DESCR.value
            )
    # recipients list file address
    parser.add_argument(
        'rec_list',
        default='source/receiver_mail.txt',
        help=Texts.LIST_DESCR.value
    )
    # day of week for delayed mailing
    parser.add_argument(
        'day',
        default=1,
        help=Texts.DAY_DESCR.value
    )
    parser.parse_args()
    mailing_list()


if __name__ == '__main__':
    main()
