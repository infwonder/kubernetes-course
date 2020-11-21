#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3
import sys
import hvac
import os
import kubernetes
import re
import time
import yaml
from base64 import b64encode
from jinja2 import Template

if len(sys.argv) != 6:
  print('Usage: ' + sys.argv[0] + ' <job_cfg_name> <javaMemory> <cluster_name> <dryRun> <vault>');
  sys.exit(1);

job, javaMemory, cluster, dryRun, vaultSync = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5];

# Load KUBECONFIG
kubeconfig = kubernetes.config.load_kube_config();

if vaultSync == 'true':
  # Login into Vault
  client = hvac.Client(url='https://or.vault.comcast.com')
  login_response = client.auth.github.login(token=os.getenv('VAULT_TOKEN'), mount_point='github_cdn-analytics' );
  
  if login_response['warnings'] == None:
    print("Vault: {}".format(login_response['auth']['policies']))
  
  # Helper functions
  def readVault(vaultPath, vault=client):
    # Maple secrets usually add kv pair with key == 'value' due to Ansible habits
    return vault.secrets.kv.v1.read_secret(path=vaultPath)['data']['value']
  
  def b64str(inStr):
    return b64encode(inStr.encode('ascii')).decode('ascii')
  
  # Read all secrets
  ch_system_password = b64str(readVault('cdn-analytics/kpipe/ch_system_password'))
  kpipe_prod_keystore_password = b64str(readVault('cdn-analytics/kpipe/kpipe_prod_keystore_password'))
  kpipe_vault_token = b64str(readVault('cdn-analytics/kpipe/kpipe_vault_token'))
  
  # Load Kubernetes
  v1 = kubernetes.client.CoreV1Api();
  
  # Test kube command "get node"
  #output = v1.list_node();
  #for k in output.items:
  #  result = list(filter(lambda x: x.type == 'InternalIP', k.status.addresses))[0];
  #  print("node: {}\taddr: {}".format(k.metadata.name, result.address));
  
  # Prepare secret
  apiVersion = 'v1'
  metadata = {'name': 'kpipe', 'namespace': 'kpipe'}
  data = {
    'ch_system_password': ch_system_password, 
    'kpipe_prod_keystore_password': kpipe_prod_keystore_password, 
    'kpipe_vault_token': kpipe_vault_token
  };
  kind = 'Secret'
  
  # Apply secret
  body = kubernetes.client.V1Secret(apiVersion, data, kind, metadata, type='Opaque')
  api_response = v1.replace_namespaced_secret(namespace='kpipe', name='kpipe', body=body)
  
  print(api_response)
else:
  print("Skip vault secret update...")

# Deploy job
cluster = 'maple-cdnlab' # for safety in lab test
print(job,javaMemory,cluster,dryRun);

# Prepare Jinja2 kpipe job template
name = '-'.join(job.split('_'))
javaMemory = int(re.sub("[^0-9]","",javaMemory));
podMemory = javaMemory * 1.2;

# Load job specific config, if not use default
ymlcfg = './data/config.yaml'
custom = {}

if os.path.exists('./data/' + job + '_config.yaml'):
  ymlcfg = './data/' + job + '_config.yaml'

with open(ymlcfg, 'r') as y:
  custom = yaml.safe_load(y)

content = {
  'appVersion': custom['appVersion'] or 'latest', 
  'maxPodCount': custom['maxPodCount'][cluster] or custom['maxPodCount']['all'] or 0, 
  'podMemory': podMemory, 
  'javaMemory': javaMemory,
  'configName': job,
  'dateTag': int(time.time()*100000),
  'jobName': name
};

if content['maxPodCount'] == 0 and 'allowZeroPod' in custom and custom['allowZeroPod'] != True:
  content['maxPodCount'] = 1

# Jinja2 template render
f = open('./data/deploy-kpipe.yaml', 'r');
t = f.read();
j2t = Template(t);
body = j2t.render(content);

# Prepare deployment 
v1 = kubernetes.client.AppsV1Api()
if dryRun != 'exec':
  api_response = v1.replace_namespaced_deployment(
     namespace='kpipe', name=name, body=yaml.safe_load(body), dry_run='All', pretty='true')
  print(body)
else:
  api_response = v1.replace_namespaced_deployment(
     namespace='kpipe', name=name, body=yaml.safe_load(body), pretty='true') 
  print(api_response)
