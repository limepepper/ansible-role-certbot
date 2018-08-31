
Certbot ansible role
=========

This role handles installing the certbot cli tool on a remote ansible node, and
 subsequently obtaining and renewing [Let's Encrypt](https://letsencrypt.org/)
 certificates using a supported authentication [plugin](https://certbot.eff.org/docs/using.html#getting-certificates-and-choosing-plugins).
It is tested against the current versions of Ubuntu, CentOS, Fedora and Debian,
and some legacy systems.

To install to your roles directory, use the ansible-galaxy cli:
```shell
$ ansible-galaxy install limepepper.certbot
```

The role assumes that the user is familiar with generating letsencrypt
certificates with certbot. Please see the [certbot](https://certbot.eff.org/docs/intro.html)
and [letsencrypt](https://letsencrypt.org/) documentation for background on using
those services, and the available options.

## Installing certbot

Certbot is installed to ansible hosts by importing the role into a play like so:

```yaml
- hosts: webservers

  tasks:
    - import_role:
        name: limepepper.certbot
```

 Or using classic role dependency syntax:

```yml
- hosts: webservers
  roles:
    - limepepper.certbot

  tasks:
    <...>
```

## Generating certificates

Importing the role exposes a module which can be used to generate and renew a certificate:

```yaml
    - certbot:
        plugin: webroot
        domain: mysite.com
        alternatives:
          - www.mysite.com
        email: certbot-dev@mywebsite.com
        document_root: /var/www/testdomain
        auto_renew_http: yes
```

If you are using the [webroot plugin](https://certbot.eff.org/docs/using.html#webroot)
you will need to place the certbot module after your tasks which setup and start
a webserver, so letsencrypt can connect back to authenticate your request. For
example:

```yaml
    - name: install httpd.conf file for mywebsite.com
      template:
        src: httpd-conf.j2
        dest: /etc/apache2/site-enabled/mywebsite.com.conf"
      register: vhost_template_conf

    - name: forcing restart of apache for this vhost
      service:
        name: apache2
        state: restarted
      when: vhost_template_conf.changed

    - certbot:
        plugin: webroot
        domain: mysite.com
        alternatives:
          - www.mysite.com
        email: certbot-dev@mywebsite.com
        document_root: /var/www/testdomain
        auto_renew_http: yes
```

Check [the wiki](https://github.com/limepepper/ansible-role-certbot/wiki) for
more detailed documentation on using the variables and the DNS plugins.

## How letsencrypt authenticates a certificate request

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

## DNS challenge, route53 plugin

A simple ansible usage for a DNS challenge is something like this; (when your
domain is on route53)

~~~yaml
---
- hosts: mygoodwebsite.com
  become: true

  tasks:
  - import_role:
      name: limepepper.certbot

  - certbot:
      domain: mygoodwebsite.com
      alternatives:
        - www.mygoodwebsite.com
      email: hello@limepepper.co.uk
      plugin: dns-route53
      auto_renew: yes
      # required if auto-renewing certificates using webonly plugin
      document_root: /var/www/mygoodwebsite.com
    environment:
      AWS_ACCESS_KEY_ID: "{{ lookup('env','AWS_ACCESS_KEY_ID') }}"
      AWS_SECRET_ACCESS_KEY: "{{ lookup('env','AWS_SECRET_ACCESS_KEY') }}"
~~~

This will output an SSL key, cert and chain file to the following location;

~~~ yml
TASK [certbot]
**************************************************************************
STDOUT:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/mygoodwebsite.com/cert.pem
   /etc/letsencrypt/live/mygoodwebsite.com/fullchain.pem
   /etc/letsencrypt/live/mygoodwebsite.com/privkey.pem

Waiting for verification...
Cleaning up challenges

~~~

and you can configure that into your virtual host configuration as required. See
here for an example of using [certbot with wordpress](). But you would use those
files something like this;

``` apache
<VirtualHost *:443>
  ServerName mygoodwebsite.com
  ServerAlias www.mygoodwebsite.com
  DocumentRoot /var/www/romfordmakerspace

  SSLEngine on

  SSLCertificateFile /etc/letsencrypt/live/mygoodwebsite.com/cert.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/mygoodwebsite.com/privkey.pem
  SSLCertificateChainFile /etc/letsencrypt/live/mygoodwebsite.com/chain.pem

  ErrorLog /var/log/httpd/mygoodwebsite.com-error.log
  CustomLog /var/log/httpd/mygoodwebsite.com-access.log combined
</VirtualHost>


```



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

    - name: create apache virtualhost for http site (used for certbot challenge)
      apache_vhost:
        ServerName: mywordpresssite2.com
        ServerAliases:
          - www.mywordpresssite2.com
        DocumentRoot: /var/www/mywordpresssite2.com
      register: mywordpresssite2_com_vhost

    - name: reload apache now if we added/changed http virtualhost
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
      # if the certificate is updated, we need to reload apache to pick it up
      notify:
        - reload apache

    - name: now we have the cert, create a ssl vhost config for it
      apache_vhost_ssl:
        ServerName: mywordpresssite2.com
        ServerAliases:
          - www.mywordpresssite2.com
        DocumentRoot: /var/www/mywordpresssite2.com
        SSLCertFile: /etc/letsencrypt/live/mygoodwebsite.com/cert.pem
        SSLCertKeyFile: /etc/letsencrypt/live/mygoodwebsite.com/privkey.pem
        SSLCertChainFile: /etc/letsencrypt/live/mygoodwebsite.com/chain.pem
      notify:
        - reload apache

~~~


