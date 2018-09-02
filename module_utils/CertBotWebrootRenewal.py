
import json
import os
import urllib
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback

# in skeleton

import tempfile

class CertBotWebrootRenewal():

  def __init__(self, module):
      self.module = module
      self._p = self.module.params

  def generate(self):

    changed=False
    result, stdout, stderr, msg = None, None, None, None

    alts = self.module.params["alternatives"]
    domain = self.module.params["domain"]
    _p = self.module.params

    document_root = self.module.params["document_root"]
    # @TODO validate docroot exists
    if not document_root:
      module.fail_json(msg='If module is webroot, document_root is required')

    if _p['debug']:
      certbot_cmd = "echo certbot certonly   \
              --webroot  \
            -w {0} ".format(document_root)
    else:
      certbot_cmd = "certbot certonly   \
              --webroot  \
            -w {0} ".format(document_root)

    if self.module.params["staging"]:
      certbot_cmd = certbot_cmd + " --staging "

    # certbot/letsencrypt seems to ignore this
    if self.module.params["port"]:
      certbot_cmd = certbot_cmd + " --http-01-port {0} ".format(self.module.params["port"])

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

    if 'Certificate not yet due for renewal; no action taken.' in stdout:
      changed=False
      msg='Certificate not yet due for renewal; no action taken.'
      stdout=None
      stderr=None

    elif 'Congratulations! Your certificate and chain have been saved' in stdout:
      changed=True
      msg='Certificate was created.'
      # stdout=None
      #stderr=None
    else:
      msg="There was some error\n\nstdout:\n"+stdout+"stderr:\n"+stderr
      changed=True

    return dict(
      changed=changed,
      msg=msg,
      result=result,
      stdout=stdout,
      stderr=stderr
    )
