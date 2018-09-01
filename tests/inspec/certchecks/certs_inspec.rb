#
#
#

# my_services = yaml(content: inspec.profile.file('services.yml')).params
vars_json = json('/var/cache/ansible/attributes/hostvars.json')

vars = vars_json.params

control 'check-attributes-01' do
  impact 0.6
  title "Check attribtues for node: #{vars['ansible_hostname']}"
  desc '      Checking the hostvars cache is sensible  '
  describe file('/var/cache/ansible/attributes/hostvars.json') do
    it { should exist }
    #  its('mode') { should cmp 0644 }
  end
end

#    ___         _   ___      _     _____       _
#   / __|___ _ _| |_| _ ) ___| |_  |_   _|__ __| |_ ___
#  | (__/ -_) '_|  _| _ \/ _ \  _|   | |/ -_|_-<  _(_-<
#   \___\___|_|  \__|___/\___/\__|   |_|\___/__/\__/__/
#

control 'check-certbot-01' do
  impact 0.6
  title "Check certbot for node: #{vars['ansible_hostname']}"
  desc '   Prevent unexpected settings.  '

  # describe file('/usr/bin/certbot') do
  #   it { should be_file }
  # end

  describe command('certbot --help') do
    its('stdout') { should match(/Certbot can obtain and install HTTPS\/TLS\/SSL certificates/) }
    its('exit_status') { should eq 0 }
  end

  describe file("/etc/letsencrypt/live/#{vars['certbot_test_domain']}/cert.pem") do
    it { should be_file }
  end

  describe file("/etc/letsencrypt/live/#{vars['certbot_test_domain']}/chain.pem") do
    it { should be_file }
  end

  describe file("/etc/letsencrypt/live/#{vars['certbot_test_domain']}/fullchain.pem") do
    it { should be_file }
  end

  describe file("/etc/letsencrypt/live/#{vars['certbot_test_domain']}/privkey.pem") do
    it { should be_file }
  end

  describe command("openssl rsa -in /etc/letsencrypt/live/#{vars['certbot_test_domain']}/privkey.pem -check -noout") do
    its('stdout') { should match(/^RSA key ok/) }
    its('exit_status') { should eq 0 }
  end

  # bunch of cert testing examples here
  # https://www.shellhacks.com/openssl-check-ssl-certificate-expiration-date/
  # https://support.asperasoft.com/hc/en-us/articles/216128468-OpenSSL-commands-to-check-and-verify-your-SSL-certificate-key-and-CSR

  describe command("echo | openssl x509 -in /etc/letsencrypt/live/#{vars['certbot_test_domain']}/cert.pem  | openssl x509 -noout -dates") do
    its('stdout') { should match(/^notBefore/) }
    its('stdout') { should match(/^notAfter/) }
    its('exit_status') { should eq 0 }
  end

  if vars.key? 'certbot_tests_staging'
    describe command("echo | openssl x509 -in /etc/letsencrypt/live/#{vars['certbot_test_domain']}/cert.pem  | openssl x509 -noout -issuer") do
      its('stdout') { should match(/^issuer/) }
      its('stdout') { should match(/Fake LE Intermediate X1$/) }
      its('exit_status') { should eq 0 }
    end
  else
    describe command("echo | openssl x509 -in /etc/letsencrypt/live/#{vars['certbot_test_domain']}/cert.pem  | openssl x509 -noout -issuer") do
      its('stdout') { should match(/^issuer/) }
      its('stdout') { should match(/C=US\/O=Let's Encrypt\/CN=Let's Encrypt Authority X3$/) }
      its('exit_status') { should eq 0 }
    end
  end

  describe command("echo | openssl x509 -in /etc/letsencrypt/live/#{vars['certbot_test_domain']}/cert.pem  | openssl x509 -noout -subject") do
    its('stdout') { should match(/#{vars['certbot_test_domain']}/) }
    its('exit_status') { should eq 0 }
  end

  # describe ssl(port: 443).protocols('ssl2') do
  #   it { should be_enabled }
  # end

end

# skiplist.each do |skip|
#   skip_control skip
# end
