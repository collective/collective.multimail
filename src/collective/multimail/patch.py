


def send(self, messageText, mto=None, mfrom=None, subject=None,
    encode=None, immediate=False, charset='utf8', msg_type=None):
    """Monkey patch MailHost send to use MultiMail instead
    """
    #assume multimail is in same folder
    multimails = self.superValues(['Multi Mail Host'])
    if len(multimails) == 0:
        return self._old_send(messageText, mto, mfrom, subject,
                              encode, immediate, charset, msg_type)
    else:
        return multimails[0].send(messageText, mto, mfrom, subject,
                              encode, immediate, charset, msg_type)