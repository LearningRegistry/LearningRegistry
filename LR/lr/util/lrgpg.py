import gnupg, logging

log = logging.getLogger(__name__)

class LRGPG(gnupg.GPG):

    def list_keys(self, keyid=None, secret=False):
        """ list the keys currently in the keyring

        >>> import shutil
        >>> shutil.rmtree("keys")
        >>> gpg = GPG(gnupghome="keys")
        >>> input = gpg.gen_key_input()
        >>> result = gpg.gen_key(input)
        >>> print1 = result.fingerprint
        >>> result = gpg.gen_key(input)
        >>> print2 = result.fingerprint
        >>> pubkeys = gpg.list_keys()
        >>> assert print1 in pubkeys.fingerprints
        >>> assert print2 in pubkeys.fingerprints

        """

        which='keys'
        if secret:
            which='secret-keys'
        args = "--list-%s --fixed-list-mode --fingerprint --with-colons" % (which,)

        if keyid is not None:
            if isinstance(keyid, list):
                args = "%s %s" % (args, " ".join(keyid))
            elif isinstance(keyid, (basestring, unicode)):
                args = "%s %s" % (args, keyid)

        args = [args]
        p = self._open_subprocess(args)

        # there might be some status thingumy here I should handle... (amk)
        # ...nope, unless you care about expired sigs or keys (stevegt)

        # Get the response information
        result = self.result_map['list'](self)
        self._collect_output(p, result, stdin=p.stdin)
        lines = result.data.decode(self.encoding,
                                   self.decode_errors).splitlines()
        valid_keywords = 'pub uid sec fpr sub'.split()
        for line in lines:
            if self.verbose:
                print(line)
            log.debug("line: %r", line.rstrip())
            if not line:
                break
            L = line.strip().split(':')
            if not L:
                continue
            keyword = L[0]
            if keyword in valid_keywords:
                getattr(result, keyword)(L)
        return result

