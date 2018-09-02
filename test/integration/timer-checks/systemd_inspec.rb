
#
skiplist = attribute('skiplist',
                     description: 'list of controls to skip',
                     default: [],
                     required: true)


# my_services = yaml(content: inspec.profile.file('services.yml')).params
vars_json = json('/var/cache/ansible/attributes/hostvars.json')

vars = vars_json.params

# systemctl list-timers
# systemctl list-timers --all

control 'renew-systemd-timer-1' do
  impact 0.6
  title "Check certbot systemd timer for #{vars['ansible_hostname']}"
  desc '  If certbot is on a system with systemd, check its timer wsa enabled '



end

control 'renew-cron-1' do
  impact 0.6
  title "Check certbot cron job for #{vars['ansible_hostname']}"
  desc '  If certbot is on a system with cron '

  # describe crontab('root') do
  #   its('commands') { should include '/path/to/some/script' }
  # end

  describe command('/var/cache/ansible/certbot/cron-report.sh') do
    its('stdout') { should match(/certbot/) }
    its('exit_status') { should eq 0 }
  end

  describe file('/etc/cron.d/certbot') do
    its('owner') { should eq 'root' }
    # its('selinux_label') { should eq 'system_u:system_r:httpd_t:s0' }
  end

  describe directory('/run/systemd/system') do
    it { should_not exist }
  end

  describe file('/run/systemd/system') do
    it { should_not exist }
  end

end

skiplist.each do |skip|
  skip_control skip
end
