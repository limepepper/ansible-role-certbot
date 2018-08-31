#!/usr/bin/python
# -*- coding: utf-8 -*-

# this line must be written exactly that way,
# as Ansible will replace it with the "imported" code
from ansible.module_utils.basic import *

from ansible.module_utils._text import to_native

from ansible.module_utils.CertBotDnsDigitalOcean import *
from ansible.module_utils.CertBotDnsRoute53 import *
from ansible.module_utils.CertBotWebroot import *
from ansible.module_utils.CertBotWebrootRenewal import *


def main():
    module = AnsibleModule(
        argument_spec={
          'domain': { 'required': True, 'type': 'str' },
          'alternatives': {
                'required': False,
                'type': 'list',
                'default': [] },
          'plugin': {
                'required': False,
                'type': 'str',
                'choices': [
                    'none',
                    'dns-route53',
                    'dns-digitalocean',
                    'webroot'],
                'default': 'none'
                },
          'email': { 'required': False, 'type': 'str' },
          'staging': { 'required': False, 'type': 'bool', 'default': False },
          'debug': { 'required': False, 'type': 'bool', 'default': False },
          'document_root': { 'required': False, 'type': 'str'},
          'port': { 'required': False, 'type': 'str'},
          'force': { 'required': False, 'type': 'bool', 'default': False },
          'auto_renew': { 'required': False, 'type': 'bool', 'default': False },
          'auto_renew_http': { 'required': False, 'type': 'bool', 'default': False },
          'systemd_template': { 'required': False, 'type': 'str' },
        },
        supports_check_mode=False
    )

    domain = module.params["domain"]

    #The request message was malformed :: Error finalizing order :: issuing precertificate: CN was longer than 64 bytes
    #Please see the logfiles in /var/log/letsencrypt for more details.

    if module.params["document_root"] and not os.path.isdir(module.params["document_root"]):
        module.fail_json(msg="document_root was provided, but isn't a directory (doc_root: {0})".format(module.params["document_root"] ))

    alternatives = module.params["alternatives"]
    staging = module.params["staging"]
    plugin = module.params["plugin"]

    if not module.params["email"]:
      module.params["email"] = "webmaster@{0}".format(domain)

    if plugin == 'dns-route53':
      plugin = CertBotDnsRoute53(module)

    elif plugin == 'dns-digitalocean':
      plugin = CertBotDnsDigitalOcean(module)

    elif plugin == 'webroot':
      plugin = CertBotWebroot(module)

    resp = plugin.generate()

    if not resp or resp['result'] != 0:
      module.warn("returning in error here")
      module.fail_json(**resp)

    if module.params["auto_renew_http"]:
      plugin_renew = CertBotWebrootRenewal(module)



    if resp and resp['result'] == 0:
      module.warn("returning in exit here2")
      module.exit_json(**resp)
    else:
      module.warn("returning in error here3")
      module.fail_json(**resp)

if __name__ == '__main__':
    main()
