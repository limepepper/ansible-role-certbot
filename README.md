
Certbot ansible role
=========

This role handles installing certbot, and subsequently obtaining and renewing
[Let's Encrypt](https://letsencrypt.org/) certificates using one or more of the
supported authentication [plugins](https://certbot.eff.org/docs/using.html#getting-certificates-and-choosing-plugins).

In order for Let's Encrypt to generate a certificate for your domain (e.g. for
use on your webserver), they require that you prove that you are in control of the domain.

You can do this in one of several ways. The 2 supported by this role are

1. By serving a specified file on your website, on port 80. This is called (http-01)
2. By creating a specified TXT record in the DNS for your domain (dns-01)

certbot is a tool to automate these authentication processes - referred to as
`challenges`

If your domain is hosted with one of the supported DNS providers, then dns-01 is the
simplist way to authenticate a request for a webserver certificate. You will need
to have access to appropriate API/cli credentials for your account. For example with
amazon route53, you set the credentials into environment variables;

~~~ yaml
    environment:
      AWS_ACCESS_KEY_ID: "{{ lookup('env','AWS_ACCESS_KEY_ID') }}"
      AWS_SECRET_ACCESS_KEY: "{{ lookup('env','AWS_SECRET_ACCESS_KEY') }}"
~~~

This role currently supports the following DNS hosting providers.

- digitalocean
- route53
- ovh (experimental)

## DNS challenge, route53 plugin

A simple ansible usage for a DNS challenge is something like this; (when your
domain is on route53)

~~~yaml
---
- hosts: romfordmakerspace.org
  become: true

  tasks:
  - import_role:
      name: limepepper.certbot

  - certbot:
      domain: romfordmakerspace.org
      alternatives:
        - www.romfordmakerspace.org
      email: hello@limepepper.co.uk
      plugin: dns-route53
      # required if auto-renewing certificate
      document_root: /var/www/romfordmakerspace.org
      auto_renew: yes
    environment:
      AWS_ACCESS_KEY_ID: "{{ lookup('env','AWS_ACCESS_KEY_ID') }}"
      AWS_SECRET_ACCESS_KEY: "{{ lookup('env','AWS_SECRET_ACCESS_KEY') }}"
~~~

This will output an SSL certificate to the following location;

`/etc/letsencrypt/live/romfordmakerspace.org/cert.pem`

and you can configure that into your virtual host configuration as required. See
here for an example of using [certbot with wordpress]()

~~~ yml
TASK [certbot] ********************************************************************************************************
task path: site-romfordmakerspace.org.yml:21
changed: [romfordmakerspace.org] => {
    "changed": true,
    "rc": 0
}

STDOUT:

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/xxx.romfordmakerspace.org-0001/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/xxx.romfordmakerspace.org-0001/privkey.pem
   Your cert will expire on 2018-11-27.
STDERR:

Saving debug log to /var/log/letsencrypt/letsencrypt.log
Found credentials in environment variables.
Plugins selected: Authenticator dns-route53, Installer None
Renewing an existing certificate
Performing the following challenges:
dns-01 challenge for xxx.romfordmakerspace.org
dns-01 challenge for xxx.www.romfordmakerspace.org
Waiting for verification...
Cleaning up challenges

~~~


## HTTP Challenge, apache webserver, certonly plugin

In this scenario, you will create a http apache virtualhost, and start the
service. The certbot will use that to stage it's http challenge response.
 Once the cert is issued, we update the apache configuration to include the SSL vhost configuration

~~~yaml

- hosts: mywordpresssite2.com
  become: yes
  roles:
     - limepepper.apache
     - limepepper.certbot

  tasks:

    - name: the http vhost to stage the http challenge response
      apache_vhost:
        ServerName: mywordpresssite2.com
        ServerAliases:
          - www.mywordpresssite2.com
        DocumentRoot: /var/www/mywordpresssite2.com
      register: mywordpresssite2_com_vhost

    - name: reload apache now if we added a vhost
      service:
        name: "{{ apache_service_name }}"
        state: reloaded
      when: mywordpresssite2_com_vhost.changed

    - name: obtain cert using certbot for mywordpresssite.com
      certbot:
        domain: mywordpresssite.com
        plugin: webroot
        alternatives:
          - www.mywordpresssite.com
        email: hello@mywordpresssite.co.uk
        # document root is required if `auto_renew` is true
        # or webroot plugin is used
        document_root: /var/www/mywordpresssite.com
        auto_renew: yes

    - name: now we have the cert, create a ssl vhost config for it
      apache_vhost_ssl:
        ServerName: mywordpresssite2.com
        ServerAliases:
          - www.mywordpresssite2.com
        DocumentRoot: /var/www/mywordpresssite2.com
        SSLCertFile: /etc/letsencrypt/live/romfordmakerspace.org/cert.pem
        SSLCertKeyFile: /etc/letsencrypt/live/romfordmakerspace.org/privkey.pem
        SSLCertChainFile: /etc/letsencrypt/live/romfordmakerspace.org/chain.pem
      notify:
        - reload apache

~~~


certbot certonly --webroot -w /var/www/example -d www.example.com -d example.com -w /var/www/other -d other.example.net -d another.other.example.net