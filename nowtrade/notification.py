import smtplib
from nowtrade import logger

class Notification(object): pass

class SMTPNotification(Notification):
    """
    SMTP-based email notifications.
    """
    def __init__(self, username,
                       password,
                       recipient,
                       server='smtp.gmail.com',
                       port=587):
        self.username = username
        self.password = password
        self.recipient = recipient
        self.server = server
        self.port = port
        self.headers = None
        self.body = None
        self.logger = logger.Logger(self.__class__.__name__)
        self.logger.info('username: %s  password: *  recipient: %s  server: %s  port: %s'
                %(username, recipient, server, port))

    def send(self, subject, body):
        self.logger.info('Sending email to %s' %self.recipient)
        self.headers = self._get_headers(subject)
        self.body = body
        self.logger.debug('Headers: %s' %self.headers)
        self.logger.debug('Body: %s' %self.body)
        self._send(self.headers, self.body)
        self.logger.debug('Email sent')

    def _get_headers(self, subject):
        headers = ['From: ' + self.username,
                   'Subject: ' + subject,
                   'To: ' + self.recipient,
                   'MIME-Version: 1.0',
                   'Content-Type: text/html']
        headers = '\r\n'.join(headers)
        return headers

    def _send(self, headers, body):
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(self.username, self.password)
        session.sendmail(self.username, self.recipient, headers + '\r\n\r\n' + body)
        session.quit()
