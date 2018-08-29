#!/usr/bin/python
# -*- coding: utf-8 -*-

# this line must be written exactly that way,
# as Ansible will replace it with the "imported" code
from ansible.module_utils.basic import *

from ansible.module_utils._text import to_native

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
                'choices': ['none', 'dns-route53', 'digitalocean'],
                'default': 'none'
                },
          'email': { 'required': False, 'type': 'str' },
          'staging': { 'required': False, 'type': 'bool', 'default': False },
        },
        supports_check_mode=False
    )
    domain = module.params["domain"]
    email = module.params["email"]
    alternatives = module.params["alternatives"]
    staging = module.params["staging"]

    if not email:
      email = "webmaster@{0}".format(domain)

    changed=False
    msg=""

    certbot_cmd = """certbot certonly   \
                --dns-route53   \
                --dns-route53-propagation-seconds 10 \
                --noninteractive  \
                --agree-tos  \
                --email {0}  \
                --expand \
                --allow-subset-of-names \
                -d {1} """.format(email, domain)

    if staging:
      certbot_cmd = certbot_cmd + " --staging "

    buffstr = ""
    for i in range(len(alternatives)):
      certbot_cmd = certbot_cmd + " -d {0} ".format(alternatives[i])

    result, stdout, stderr = module.run_command(certbot_cmd)

    if 'Certificate not yet due for renewal; no action taken.' in stdout:
      changed=False
      msg='Certificate not yet due for renewal; no action taken.'
      # stdout=None
      # stderr=None
    else:
      changed=True

    module.exit_json(   changed=changed,
                        rc=result,
                        stdout=stdout,
                        msg=msg,
                        stderr=stderr,
                        cmd=certbot_cmd)

if __name__ == '__main__':
    main()
