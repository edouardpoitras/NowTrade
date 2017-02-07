"""
The notification module has classes that make notifying the user of events
(such as entering/exiting a trade) a bit easier.
"""
import smtplib
from nowtrade import logger

class Notification(object):
    """
    The base notification class.
    """
    pass

class SMTPNotification(Notification):
    """
    SMTP-based email notifications.
    """
    def __init__(self, username, password, recipient, server='smtp.gmail.com', port=587):
        self.username = username
        self.password = password
        self.recipient = recipient
        self.server = server
        self.port = port
        self.session = self._get_session()
        self.headers = None
        self.body = None
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('username: %s  password: *  recipient: %s  server: %s  port: %s'
                         %(username, recipient, server, port))

    def send(self, subject, body):
        """
        Sends the email out with the specified subject and body.
        """
        self.logger.info('Sending email to %s' %self.recipient)
        self.headers = self._get_headers(subject)
        self.body = body
        self.logger.debug('Headers: %s' %self.headers)
        self.logger.debug('Body: %s' %self.body)
        self._send(self.headers, self.body)
        self.logger.debug('Email sent')

    def _get_headers(self, subject):
        """
        Helper method to generate the email headers.
        """
        headers = ['From: ' + self.username,
                   'Subject: ' + subject,
                   'To: ' + self.recipient,
                   'MIME-Version: 1.0',
                   'Content-Type: text/html']
        return '\r\n'.join(headers)

    def _get_session(self):
        """
        Simple method to retrieve the email session.
        """
        return smtplib.SMTP(self.server, self.port)

    def _send(self, headers, body):
        """
        Low level method that actually does the sending of the email.
        Should use send() instead.
        """
        self.session.ehlo()
        self.session.starttls()
        self.session.ehlo()
        self.session.login(self.username, self.password)
        self.session.sendmail(self.username, self.recipient, headers + '\r\n\r\n' + body)
        self.session.quit()
