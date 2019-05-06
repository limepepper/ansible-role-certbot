
import json
import os
import urllib
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback

# in skeleton

import os
import tempfile


class CertBotDnsRoute53():

    def __init__(self, module):
        self.module = module
        self._p = self.module.params

    def generate(self):

        changed = False
        result, stdout, stderr, msg = None, None, None, None

        # key = os.environ['AWS_ACCESS_KEY_ID']
        # self.module.warn("key {0}".format(key))

        alts = self.module.params["alternatives"]
        domain = self.module.params["domain"]
        _p = self.module.params

        if _p['debug']:
            certbot_cmd = "echo certbot certonly   \
                --dns-route53   \
                --dns-route53-propagation-seconds 10 "
        else:
            certbot_cmd = "certbot certonly   \
                --dns-route53   \
                --dns-route53-propagation-seconds 10 "

        if self.module.params["staging"]:
            certbot_cmd = certbot_cmd + " --staging "

        certbot_cmd = certbot_cmd + "  --noninteractive  \
                --agree-tos  \
                --email {0}  \
                --expand \
                --allow-subset-of-names \
                -d {1} ".format(_p['email'], _p['domain'])

        for i in range(len(alts)):
            certbot_cmd = certbot_cmd + " -d {0} ".format(alts[i])

        if self.module.params["force"]:
            certbot_cmd = certbot_cmd + " --force-renewal "

        self.module.warn("{0}".format(certbot_cmd))

        result, stdout, stderr = self.module.run_command(certbot_cmd)

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

        elif stdout.startswith('certbot certonly'):
            changed = True
            msg = 'module is in debug mode, no cmd was run'
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
