# my_services = yaml(content: inspec.profile.file('services.yml')).params
vars_json = json('/var/cache/ansible/attributes/hostvars.json')

vars = vars_json.params

control 'check-attributes-1' do
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

  describe file(vars['certbot_path']) do
    it { should exist }
    it { should be_allowed('execute') }
    # it { should be_allowed('execute', by: 'root') }
  end

  describe command('certbot --help') do
    its('stdout') { should match(/Certbot can obtain and install HTTPS\/TLS\/SSL certificates/) }
    its('exit_status') { should eq 0 }
  end

  describe command('certbot --version  2>&1') do
    its('stdout') { should match(/certbot/) }
    its('stderr') { should eq '' }
    its('exit_status') { should eq 0 }
  end

  describe command('certbot plugins') do
    its('stdout') { should match(/^\* dns-route53/) }
    its('exit_status') { should eq 0 }
  end

  describe command('certbot plugins') do
    its('stdout') { should match(/^\* dns-digitalocean/) }
    its('exit_status') { should eq 0 }
  end

  describe file('/etc/letsencrypt') do
    it { should be_directory }
  end

  describe command('certbot plugins') do
    its('stdout') { should match(/^\* dns-digitalocean/) }
    its('exit_status') { should eq 0 }
  end
end

# skiplist.each do |skip|
#   skip_control skip
# end
