import os
# import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('proxy', help='IP to proxy to (e.g. "example.com" / "192.168.1.2" )')
args = parser.parse_args()
if not args.proxy.startswith('http://'):  # use the first parameter as the ip
    ip = 'http://' + args.proxy
else:
    ip = args.proxy
cwd = os.getcwd()  # get current working directory
pPath = ''  # path to proxy to
print("Creating nginx.conf file")
conf = open('nginx.conf', 'w+')  # create the .conf file
print("Writing defaults to main context")
defaults = open("defaults.txt")  # copy from defaults.text
for line in defaults:  # copy defaults into .conf file #TODO find a way to do this without a .txt file
    conf.write(line)
defaults.close()
conf.write('\n')  # new line after defaults
print("Scanning for files and dedicating proxy")
# route main IP to main site IP
conf.write('\t\tlocation ~* ^/$ {{\n\t\t\t rewrite .* / break;\n\t\t\tproxy_pass {0};\n\t\t}}\n'.format(ip))
for root, dirs, files in os.walk(cwd):  # traverse directories
    for file in files:
        # don't create a listing for the script, defaults file or the .conf file
        if file != 'nginprox.py' and file != 'defaults.txt' and file != 'nginx.conf':
            pPath = ((root.replace(cwd, '') + os.sep + file).replace('\\', '/'))  # define the pPath in the right syntax
            conf.write ("\t\tlocation = {0} {{\n\t\t\t proxy_pass {1};  \n\t\t}}\n".format(pPath, ip+pPath))
print("Creating exceptions")
# RegEx to match allowed files #TODO make this better
conf.write("\t\tlocation ~* .*\\.(gif|png|jp.g)$ {{\n\t\t\t proxy_pass {0};\n\t\t}}\n".format(ip))
print("Appending a 'catch-all'")
# catch all, throw to 404
conf.write('\t\tlocation ~* .*$ {{\n\t\t\t rewrite .* /404 break;\n\t\t\tproxy_pass {0};\n\t\t}}\n'.format(ip))
conf.write("\t}\n}")  # end the http and server open brackets
print("finished :)")
