import gnupg, logging

log = logging.getLogger(__name__)

class LRGPG(gnupg.GPG):

    def list_keys(self, keyid=None, secret=False):

        result = super(LRGPG, self).list_keys(secret)

        if keyid is not None:

            if(isinstance(keyid, str)):
                keyid = [keyid]

            result = [i for i in result if i['fingerprint'][-16:] in keyid]


        return result




