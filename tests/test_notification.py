from nowtrade.notification import SMTPNotification
import unittest

class MockSMTPNotification(SMTPNotification):
    def __init__(self, username, password, recipient):
        SMTPNotification.__init__(self, username, password, recipient)
        self.session = MockSMTPSession()

    def _get_session(self):
        pass

class MockSMTPSession:
    def ehlo(self): pass
    def starttls(self): pass
    def login(self, username, password): pass
    def sendmail(self, username, recipient, content): pass
    def quit(self): pass

class TestSMTPNotification(unittest.TestCase):
    def test_initialization(self):
        mock_notification = MockSMTPNotification('USERNAME', 'PASSWORD', 'RECIPIENT@EMAIL.COM')
        mock_notification.send('SUBJECT', 'BODY')
        headers = mock_notification.headers.split('\r\n')
        self.assertEquals(headers[0], 'From: USERNAME')
        self.assertEquals(headers[1], 'Subject: SUBJECT')
        self.assertEquals(headers[2], 'To: RECIPIENT@EMAIL.COM')
        self.assertEquals(headers[3], 'MIME-Version: 1.0')
        self.assertEquals(headers[4], 'Content-Type: text/html')
        self.assertEquals(mock_notification.body, "BODY")

if __name__ == "__main__":
    unittest.main()
