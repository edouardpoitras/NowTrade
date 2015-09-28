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
        self.logger = Logger(self.__class__.__name__)
        self.logger.info('username: %s  password: *  recipient: %s  server: %s  port: %s'
                %(username, password, recipient, server, port))

    def send(self, subject, body):
        self.logger.info('Sending email to %s' %self.recipient)
        headers = ['From: ' + self.username,
                   'Subject: ' + subject,
                   'To: ' + self.recipient,
                   'MIME-Version: 1.0',
                   'Content-Type: text/html']
        headers = '\r\n'.join(headers)
        self.logger.debug('Headers: %s' %headers)
        self.logger.debug('Body: %s' %body)
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(self.username, self.password)
        session.sendmail(self.username, self.recipient, headers + '\r\n\r\n' + body)
        session.quit()
        self.logger.debug('Email sent')

if __name__ == '__main__':
    SMTPNotification('user@gmail.com', 'password', \
                     'recipient@email.com').send('Test Subject', 'Test Email Body')
