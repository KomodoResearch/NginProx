import os
# import sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--proxy', default='http://127.0.0.1', help='IP to proxy to (e.g. "example.com" / '
                                                                      '"192.168.1.2" ) on default using localhost')
parser.add_argument('-r', '--root-folder', default=os.getcwd(), help="Specify the web-server's root directory (e.g "
                                                                     "/var/www/html), by default using current "
                                                                     "directory")
parser.add_argument('-I', '--install', action='store_true', help="Use -I to install the nginx and set it up with "
                                                                 "reverse proxy")
args = parser.parse_args()
if not args.proxy.startswith('http://'):  # use the first parameter as the ip
    ip = 'http://' + args.proxy
else:
    ip = args.proxy
cwd = args.root_folder  # set the root folder to the arg parsed
pPath = ''  # path to proxy to
print("Creating nginx.conf file")
conf = open('nginx.conf', 'w+')  # create the .conf file
print("Writing defaults to main context")
defaults = open("defaults")  # copy nginx start of settings file into conf
for line in defaults:  # copy defaults into .conf file
    conf.write(line)
defaults.close()
print("Scanning for files and dedicating proxy")
conf.write('\t\tlocation ~* ^/$ {{\n\t\t\trewrite .* / break;\n\t\t\tproxy_pass {0};\n\t\t}}\n'.format(ip))  #
# route main IP to main site IP
for root, dirs, files in os.walk(cwd):  # traverse directories
    for file in files:
        # don't create a listing for the script, defaults file or the .conf file
        if file != 'nginprox.py' and file != 'defaults.txt' and file != 'nginx.conf':
            pPath = ((root.replace(cwd, '') + os.sep + file).replace('\\', '/'))  # define the pPath in the right syntax
            conf.write("\t\tlocation = {0} {{\n\t\t\t proxy_pass {1};  \n\t\t}}\n".format(pPath, ip + pPath))
print("Creating exceptions")
# RegEx to match allowed files #TODO make this better
conf.write("\t\tlocation ~* .*\\.(gif|png|jp.g)$ {{\n\t\t\t proxy_pass {0};\n\t\t}}\n".format(ip))
print("Appending a 'catch-all'")
# catch all, throw to 404
conf.write('\t\tlocation ~* .*$ {{\n\t\t\trewrite .* /404 break;\n\t\t\tproxy_pass {0};\n\t\t}}\n'.format(ip))
conf.write("\t}\n}")  # end the http and server open brackets
print("finished :)")


def install_ngn():
    """Installs the Nginx service and checks that it is active"""
    systemctl = ['systemctl', '-l', '--type', 'service', '--all']  # command to list all services on the device
    grep = ['grep', 'nginx']  # command to grep for nginx
    systemctl_process = subprocess.Popen(systemctl, shell='true', stdout=subprocess.PIPE)  # run the systemctl command
    grep_process = subprocess.Popen(grep, stdin=systemctl_process.stdout, universal_newlines='true',
                                    stdout=subprocess.PIPE)  # run the grep command on the previous command
    output = grep_process.communicate()  # grab output
    if output is not None:  # TODO install nginx
    else:
        return False  # use as flag for "is nginx already installed"
