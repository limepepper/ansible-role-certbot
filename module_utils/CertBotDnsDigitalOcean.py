
import json
import urllib
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback

# in skeleton


import os
import tempfile
import shutil
import tempfile


class CertBotDnsDigitalOcean():

    def __init__(self, module):
        self.module = module
        self._p = self.module.params

    def generate(self):

        changed = False
        result, stdout, stderr, msg = None, None, None, None

        alts = self.module.params["alternatives"]
        domain = self.module.params["domain"]
        _p = self.module.params

        credsfile = "digoc_creds.ini"
        basedir = tempfile.mkdtemp()
        # self.module.warn("dir name {0}".format(basedir))
        tmpfile = os.path.join(basedir, credsfile)

        try:
            f = open(tmpfile, "w+")
            tokenstr = ""
            token = os.environ['DIGITALOCEAN_ACCESS_TOKEN']
            tokenstr = tokenstr + "dns_digitalocean_token = {0}".format(token)
            f.write(tokenstr)
            f.close()

            # self.module.warn("{0}".format(tokenstr))

            if _p['debug']:
                certbot_cmd = "echo certbot certonly   \
                  --dns-digitalocean  \
                --dns-digitalocean-credentials {0}  ".format(tmpfile)
            else:
                certbot_cmd = "certbot certonly   \
                  --dns-digitalocean  \
                --dns-digitalocean-credentials {0}  ".format(tmpfile)

            if self.module.params["staging"]:
                certbot_cmd = certbot_cmd + " --staging "

            if self.module.params["force"]:
                certbot_cmd = certbot_cmd + ' --force-renewal  '

            certbot_cmd = certbot_cmd + "  --noninteractive  \
                    --agree-tos  \
                    --email {0}  \
                    --expand \
                    --allow-subset-of-names \
                    -d {1} ".format(_p['email'], _p['domain'])

            for i in range(len(alts)):
                certbot_cmd = certbot_cmd + " -d {0} ".format(alts[i])

            # self.module.warn("{0}".format(certbot_cmd))

            result, stdout, stderr = self.module.run_command(certbot_cmd)

        finally:
            f.close()
            shutil.rmtree(basedir)

        if 'Certificate not yet due for renewal; no action taken.' in stdout:
            changed = False
            msg = 'Certificate not yet due for renewal; no action taken.'
            stdout = None
            stderr = None

        elif 'Congratulations! Your certificate and chain have been saved' in stdout:
            changed = True
            msg = 'Certificate was created.'
            # stdout=None
            # stderr=None
        else:
            msg = "There was some error\n\nstdout:\n"+stdout+"stderr:\n"+stderr
            changed = True

        return dict(
            changed=changed,
            msg=msg,
            result=result,
            stdout=stdout,
            stderr=stderr
        )
