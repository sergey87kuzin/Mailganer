from enum import Enum


class Texts(Enum):
    HEADER = 'Happy New Year'
    BODY = 'Hello, {name} {surname}! You are impossible!'
    FULL_DESCR = 'program for send email to each receiver in the list'
    LIST_DESCR = 'recipients list file address'
    DAY_DESCR = 'day of week for delayed mailing'
