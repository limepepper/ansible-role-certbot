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

  describe ssl(port: 443).protocols('ssl2') do
    it { should_not be_enabled }
  end

  describe ssl(port: 443) do
    it { should be_enabled }
    # its('protocols') { should_not include 'ssl2' }
  end

  #should be_in

  describe ssl(port: 443).protocols('ssl2') do
    proc_desc = "on node ==target_hostname} runn)"
    it(proc_desc) { should_not be_enabled }
    it { should_not be_enabled }
  end

  # describe ssl(port: 443).ciphers(/rc4/i) do
  #   # it(proc_desc) { should_not be_enabled }
  #   #its('protocols') { should eq 'ssl2' }
  #   it { should_not be_enabled }
  # end

  # describe ssl(port: 443) do
  #   # it(proc_desc) { should_not be_enabled }
  #   its('ciphers') { should eq '/rc4/i' }
  #   #its('protocols') { should eq 'ssl2' }
  # end

end


#                           _            _            _
#     __ _ _ __   __ _  ___| |__   ___  | |_ ___  ___| |_ ___
#    / _` | '_ \ / _` |/ __| '_ \ / _ \ | __/ _ \/ __| __/ __|
#   | (_| | |_) | (_| | (__| | | |  __/ | ||  __/\__ \ |_\__ \
#    \__,_| .__/ \__,_|\___|_| |_|\___|  \__\___||___/\__|___/
#         |_|

control 'check-apache-10' do
  impact 0.6
  title "Check apache for node: #{vars['ansible_hostname']}"
  desc '   Prevent unexpected settings.  '

  describe service(vars['apache_service']) do
    it { should be_enabled }
    it { should be_installed }
    it { should be_running }
  end

  url = "https://#{vars['certbot_test_domain']}/index.html"

  describe http(url, ssl_verify: false) do
    its('status') { should eq 200 }
    its('body') { should match(/This is a test page YYY/) }
    # its('headers.name') { should eq 'header' }
    its('headers.Content-Type') { should match(/text\/html/) }

  end

  # | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'
  # openssl s_client -showcerts -servername www.example.com -connect www.example.com:443 </dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'

  describe command("echo | openssl s_client -servername #{vars['certbot_test_domain']} -connect #{vars['certbot_test_domain']}:443 2>/dev/null | openssl x509 -noout -subject") do
    its('stdout') { should match(/#{vars['certbot_test_domain']}/) }
    its('exit_status') { should eq 0 }
  end

  # describe command("echo | openssl s_client -servername #{vars['certbot_test_domain']} -connect #{vars['certbot_test_domain']}:443 2>/dev/null | openssl x509 -noout -dates") do
  #   its('stdout') { should match(/^notBefore/) }
  #   its('stdout') { should match(/^notAfter/) }
  #   its('exit_status') { should eq 0 }
  # end

  describe command("echo | openssl s_client -servername #{vars['certbot_test_domain']} -connect #{vars['certbot_test_domain']}:443 2>/dev/null | openssl x509 -noout -startdate") do
    its('stdout') { should match(/^notBefore/) }
    # its('stdout') { should match(/^notAfter/) }
    its('exit_status') { should eq 0 }
  end

  # https://www.openssl.org/docs/manmaster/man1/x509.html

  describe command("echo | openssl s_client -servername #{vars['certbot_test_domain']} -connect #{vars['certbot_test_domain']}:443 2>/dev/null | openssl x509 -noout -enddate") do
    # its('stdout') { should match(/^notBefore/) }
    its('stdout') { should match(/^notAfter/) }
    its('exit_status') { should eq 0 }
  end

  # describe apache do
  #   its('user') { should eq vars['apache_user'] }
  # end

  # describe package('php') do
  #   it { should_not be_installed }
  # end

  describe port(80) do
    it { should be_listening }
  end

  describe file('/tmp') do
    it { should be_directory }
  end

  # describe file('hello.txt') do
  #   its('content') { should match 'Hello World' }
  # end
end

# skiplist.each do |skip|
#   skip_control skip
# end
