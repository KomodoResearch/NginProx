import os
# import sys
import argparse
import subprocess


def ngn_check():
    """checks for nginx on the system True if installed"""
    systemctl = 'systemctl -l --type service --all'.split()  # command to list all services on the device
    grep = 'grep nginx'.split()  # command to grep for nginx
    systemctl_process = subprocess.Popen(systemctl, stdout=subprocess.PIPE)  # run the systemctl command
    systemctl_process.wait()  # wait for systemctl_process to end
    grep_process = subprocess.Popen(grep, stdin=systemctl_process.stdout, stdout=subprocess.PIPE,
                                    universal_newlines=True)  # run the grep command on the systemctl command
    output = grep_process.communicate()[0]  # wait for grep_process to end and grab its stdout to output
    if output is not '':
        return True
    else:
        return False


def ngn_install():
    apt_get_update = 'sudo apt-get update'.split()
    apt_get_install = 'sudo apt-get -y install nginx'.split()
    update_process = subprocess.Popen(apt_get_update, stdout=subprocess.PIPE)
    update_process.wait()
    install_process = subprocess.Popen(apt_get_install, stdout=subprocess.PIPE)
    install_process.wait()
    return


def ngn_bind_port():
    restart = "sudo systemctl restart nginx".split()  # restart nginx command
    default_in = open("/etc/nginx/sites-enabled/default", 'rt').read()  # read the default configuration
    default_in = default_in.replace("listen 80", "listen 8888", 1)  # replace the first appearance of the ipv4 port bind
    default_in = default_in.replace("listen [::]:80", "listen [::]:8888",
                                  1)  # replace the first appearance of the ipv6 port bind
    default_out = open("/etc/nginx/sites-enabled/default", 'wt')  # temp file with new settings
    default_out.write(default_in)  # wrtite tmp file to real file
    default_out.close()
    subprocess.Popen(restart, stdout=subprocess.PIPE)  # restart nginx


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--proxy', default='http://127.0.0.1', help='IP to proxy to (e.g. "example.com" / '
                                                                      '"192.168.1.2" ) on default using localhost')
parser.add_argument('-r', '--root-folder', default=os.getcwd(), help="Specify the web-server's root directory (e.g "
                                                                     "/var/www/html), by default using current "
                                                                     "directory")
parser.add_argument('-i', '--install', action='store_true', help="Use -I to install the nginx and set it up with "
                                                                 "reverse proxy")
args = parser.parse_args()
if not args.proxy.startswith('http://'):  # use the first parameter as the ip
    ip = 'http://' + args.proxy
else:
    ip = args.proxy
cwd = args.root_folder  # set the root folder to the arg parsed
if args.install:
    print("Checking if Nginx is already installed")
    if not ngn_check():
        print("Installing Nginx")
        ngn_install()
    else:
        input("Nginx already installed, press enter to create .conf file and attach it to existing nginx installation")
pPath = ''  # path to proxy to
print("Creating nginx.conf file")
conf = open('nginx.conf', 'w+')  # create the .conf file
print("Writing defaults to main context")
defaults = open("defaults")  # copy nginx start of settings file into conf
for line in defaults:  # copy defaults into .conf file
    conf.write(line)
defaults.close()
print("Traversing paths and dedicating proxy")
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


