import subprocess
import sys
import time

import requests

CLOUDALIZER_IP = "35.196.167.141"
CLUSTER_IP = "10.21.55.37"
VM_UUID = "314cecaf-03cc-437d-9828-32e99fd474a9"


def send_mail(address, sender, subject, body):
  cmd = "echo \"%s\" | mail -v -s \"%s\" -r \"%s\" %s" % (
    body, subject, sender, address)
  subprocess.check_call(cmd, shell=True)


def toggle_vm_power():
  s = requests.Session()
  s.auth = ('admin', 'techX2018!')

  url = "https://%s:9440/api/nutanix/v2.0/vms/%s" % (
    CLUSTER_IP, VM_UUID)
  response = s.get(url, verify=False)
  vm_info = response.json()

  vm_is_on = vm_info.get("power_state", "").lower() == "on"
  if vm_is_on:
    current_state = "on"
    transition = "off"
    print "VM is ON,  and will be powered OFF"
  else:
    current_state = "off"
    transition = "on"

  print "VM is %s, and will be powered %s" % (current_state, transition)
  response = s.post(url + "/set_power_state",
                    json={"transition": transition.upper()},
                    verify=False)
  task_info = response.json()
  print "Created task '%s'" % task_info.get("task_uuid")
  send_mail(address="7209332478@vtext.com",
            sender="zero_cool@aol.com",
            subject="Hey bro, your VM turned %s" % transition.upper(),
            body="Boot up, or shut up!\n\nXOXO,\n\n/zero_cool")


def get_vms_status():
  s = requests.Session()
  s.auth = ('admin', 'techX2018!')

  url = "https://%s:9440/api/nutanix/v2.0/vms" % CLUSTER_IP
  response = s.get(url, verify=False)
  vms_info = response.json()

  powered_on_vms = []
  powered_off_vms = []
  for vm_info in vms_info.get("entities", []):
    if vm_info.get("power_state", "").lower() == "on":
      powered_on_vms.append(vm_info)
    else:
      powered_off_vms.append(vm_info)

  print "There are %d on, %d off VMs" % (len(powered_on_vms),
                                         len(powered_off_vms))
  on_str = "%d %s" % (len(powered_on_vms),
                      "VM is" if len(powered_on_vms) == 1 else "VMs are")
  off_str = "%d %s" % (len(powered_off_vms),
                      "VM is" if len(powered_off_vms) == 1 else "VMs are")
  send_mail(address="7209332478@vtext.com",
            sender="zero_cool@aol.com",
            subject="Whoa, %s on, %s off" % (on_str, off_str),
            body="Nice watch - can you hack one of those Gibson's with it?\n"
                 "\nPeace,\n\n/zero_cool")


def get_host_alerts():
  s = requests.Session()
  s.auth = ('admin', 'techX2018!')

  url = "https://%s:9440/api/nutanix/v2.0/hosts/alerts" % CLUSTER_IP
  response = s.get(url, verify=False)
  host_alerts_info = response.json()

  all_alerts = []
  acked_alerts = []
  for host_alert in host_alerts_info.get("entities", []):
    if host_alert.get("acknowledged"):
      acked_alerts.append(host_alert)
    else:
      all_alerts.append(host_alert)

  if len(all_alerts) - len(acked_alerts) == 0:
    subject = "No host alerts - keep hacking, dude!"
  else:
    subject = "%d outstanding alerts :(" % (len(all_alerts) - len(acked_alerts))

  send_mail(address="7209332478@vtext.com",
            sender="zero_cool@aol.com",
            subject=subject,
            body="/zero_cool")


if __name__ == '__main__':
  while True:
    try:
      response = requests.get("http://%s/cmd" % CLOUDALIZER_IP)
      if response.status_code == 200:
        action = response.json()
        print "Got action '%s'" % action
        if action == "power":
          toggle_vm_power()
        elif action == "availability":
          get_vms_status()
        elif action == "alert":
          get_host_alerts()
        else:
          print "Unknown action '%s'" % action
      else:
        time.sleep(5)
    except Exception as exc:
      type, value, traceback = sys.exc_info()
      print "Got an exception"
      print traceback
      print "Continuing"
