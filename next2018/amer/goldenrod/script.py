#!/usr/bin/env python
# script.py -*-python-*-

import json
import requests
import sys
import time
sys.path.append("./automation/solution/")

from V3 import *
from config import *
from manageBlueprint import *

class Connector(object):
  def __init__(self):
    self.connection = Connection(User(USER, PASSWD),
                                 Host(IPADDRESS, PORT))
    self.data = { 'filter': '',
                  'offset': 0,
                  'length': 20 }
    self.dead = set()

  def _show_list(self, items):
    for item in items:
      print 'type: ' + str(item.type)
      print 'name: ' + str(item.name)
      #print 'description: ' + str(self.description)
      print 'ipaddress: ' + str(item.ipaddress)
      print 'uuid: ' + str(item.uuid)
      print 'power state: ' + str(item.powerState)
      print 'memory: ' + str(item.memory)
      print ' '

  def get_vm_count(self):
    vms = VirtualMachineService().getVMS(self.connection, self.data)
    return len(vms)

  def get_load(self):
    try:
      r = requests.get(
        'https://%s:%s/PrismGateway/services/rest/v2.0/cluster/' % (PEIPADDRESS,
                                                                    PORT),
        verify=False,
        auth=(USER, PASSWD))

      r.raise_for_status()
    except requests.HTTPError as ex:
      print "Failed to create %s\n" % str(ex)

    j = r.json()
    return int(j['stats']['hypervisor_cpu_usage_ppm']) / 1000000.0 * 100.0

  def get_blueprintlist(self):
    blueprints = BlueprintService().getBlueprints(self.connection,
                                                  self.data)
    for bp in blueprints:
      bp.show()

  def get_apps(self, kill=False):
    apps = ApplicationService().getApplications(self.connection, self.data)
    for app in apps:
      if app.instance['metadata']['name'].startswith('FAH-'):
        name = app.instance['metadata']['name']
        uuid = app.instance['metadata']['uuid']
        elapsed = int(time.time()) - int(name[4:])
        if kill and elapsed > 300 and uuid not in self.dead:
          self.dead.add(uuid)
          print 'DELETE', name, uuid, 'ELAPSED', elapsed
          ApplicationService().deleteApplication(self.connection, app)

  def launch_blueprint(self, name):
    headers = {'Content-type': 'application/json','Accept': 'application/json'}
    try:
      r = requests.get(
        'https://10.21.72.39:9440/api/nutanix/v3/blueprints/bc3f1e73-c846-a4af-f7fa-ee3cd9e852e7',
        verify=False,
        headers=headers,
        auth=(USER, PASSWD))
      r.raise_for_status()
    except requests.HTTPError as ex:
      print "Failed to create %s\n" % str(ex)

    payload = r.json()
    del payload['spec']['name']
    del payload['status']
    payload['spec']['application_name'] = name
    payload['spec']['app_profile_reference'] = {
      'kind': 'app_profile',
      'uuid':payload['spec']['resources']['app_profile_list'][0]['uuid']
    }

    try:
      r = requests.post(
        'https://10.21.72.39:9440/api/nutanix/v3/blueprints/bc3f1e73-c846-a4af-f7fa-ee3cd9e852e7/launch',
        verify=False,
        headers=headers,
        auth=(USER, PASSWD),
        data=json.dumps(payload))
      r.raise_for_status()
    except requests.HTTPError as ex:
      print "Failed to create %s\n" % str(ex)

#    print r
#    print r.json()

if __name__ == "__main__":
  c = Connector()
  c.get_blueprintlist()
#  c.get_apps(kill=True)
#  sys.exit(0)
#  c.launch_blueprint('FAHClientBP', 'ACTIVE',
#                     'test1')
  while True:
    load = c.get_load()
    vmcount = c.get_vm_count()
    print "%d vms, CPU load = %0.3f%%" % (vmcount, load)
    if load < 50:
      name = 'FAH-%d' % int(time.time())
      print 'LAUNCH', name
      c.launch_blueprint(name)
    if True or load > 50:
      c.get_apps(kill=True)
    time.sleep(20)
