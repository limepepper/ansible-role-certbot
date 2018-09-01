#
#
#

# my_services = yaml(content: inspec.profile.file('services.yml')).params
vars_json = json('/var/cache/ansible/attributes/hostvars.json')

vars = vars_json.params


#    ___         _   ___      _     _____       _
#   / __|___ _ _| |_| _ ) ___| |_  |_   _|__ __| |_ ___
#  | (__/ -_) '_|  _| _ \/ _ \  _|   | |/ -_|_-<  _(_-<
#   \___\___|_|  \__|___/\___/\__|   |_|\___/__/\__/__/
#

control 'check-plugin-dns-digitalocean-1' do
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

  # describe ssl(port: 443).protocols('ssl2') do
  #   it { should be_enabled }
  # end

end

# skiplist.each do |skip|
#   skip_control skip
# end
