import os
# import sys
import argparse
import subprocess
import re


def ngn_check():
    """checks for nginx on the system, True if installed"""
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
    """installs the nginx service"""
    apt_get_update = 'sudo apt-get update'.split()
    apt_get_install = 'sudo apt-get -y install nginx'.split()
    update_process = subprocess.Popen(apt_get_update, stdout=subprocess.PIPE)
    update_process.wait()
    install_process = subprocess.Popen(apt_get_install, stdout=subprocess.PIPE)
    install_process.wait()
    return


def ngn_bind_port(port="8888"):
    """Changes the nginx port to port supplied (8888 by default)"""
    restart = "sudo systemctl restart nginx".split()  # restart nginx command
    default_in = open("/etc/nginx/sites-enabled/default", 'rt').read()  # read the default configuration
    default_in = re.sub('listen ([0-9]){1,5}', 'listen {0}'.format(port), default_in, count=1)  # replace the first
    # appearance of the ipv4 port bind
    default_in = re.sub("listen \[::\]:([0-9]){1,5}", 'listen [::]:{0}'.format(port), default_in, count=1)  # replace
    # the first appearance of the ipv6 port bind
    default_out = open("/etc/nginx/sites-enabled/default", 'wt')  # temp file with new settings
    default_out.write(default_in)  # write tmp file to real file
    default_out.close()
    subprocess.Popen(restart, stdout=subprocess.PIPE)  # restart nginx


def argparser():
    """argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--proxy', default='http://127.0.0.1', help='IP to proxy to (e.g. "example.com" / '
                                                                          '"192.168.1.2" ) on default using localhost')
    parser.add_argument('-r', '--root-folder', default=os.getcwd(), help="Specify the web-server's root directory (e.g "
                                                                         "/var/www/html), by default using current "
                                                                         "directory")
    parser.add_argument('-i', '--install', action='store_true', help="Use -i to install the nginx and set it up with "
                                                                     "reverse proxy")
    return_args = parser.parse_args()
    return return_args


def write_defaults(output):
    """copy content of default file into conf file"""
    print("Writing defaults to main context")
    defaults = open("defaults")  # copy nginx start of settings file into conf
    for line in defaults:  # copy defaults into .conf file
        output.write(line)
    defaults.close()
    return


def proxy_dedicator(output, ip, cwd):
    """main proxy function"""
    print("Traversing paths and dedicating proxy")
    output.write('\t\tlocation ~* ^/$ {{\n\t\t\trewrite .* / break;\n\t\t\tproxy_pass {0};\n\t\t}}\n'.format(ip))  #
    # route main IP to main site IP
    for root, dirs, files in os.walk(cwd):  # traverse directories
        for file in files:
            # don't create a listing for the script, defaults file or the .conf file
            if file != 'nginprox.py' and file != 'defaults.txt' and file != 'nginx.conf':
                pPath = (
                    (root.replace(cwd, '') + os.sep + file).replace('\\', '/'))  # define the pPath in the right syntax
                output.write("\t\tlocation = {0} {{\n\t\t\t proxy_pass {1};  \n\t\t}}\n".format(pPath, ip + pPath))
    print("Creating exceptions")
    # RegEx to match allowed files #TODO change this to a customizable function
    output.write("\t\tlocation ~* .*\\.(gif|png|jp.g)$ {{\n\t\t\t proxy_pass {0};\n\t\t}}\n".format(ip))
    print("Appending a 'catch-all'")
    # catch all, throw to 404
    output.write('\t\tlocation ~* .*$ {{\n\t\t\trewrite .* /404 break;\n\t\t\tproxy_pass {0};\n\t\t}}\n'.format(ip))
    output.write("\t}\n}")  # end the http and server open brackets


def main():
    args = argparser()
    if not args.proxy.startswith('http://'):  # use the first parameter as the ip and check for 'http://'
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
            input(
                "Nginx already installed, press enter to create .conf file and attach it to existing nginx installation")
        ngn_bind_port()  # change port to 8888 on default so nginx wont crash when clashing with existing web server
    print("Creating nginx.conf file")
    conf = open('nginx.conf', 'w+')
    write_defaults(conf)
    if args.install:
        conf.write("\t\tlisten 8888;\n")
    proxy_dedicator(conf, ip, cwd)
    if args.install:
        print("copying .conf file to nginx directory")
        subprocess.Popen("sudo cp nginx.conf /etc/nginx/nginx.conf".split(), stdout=subprocess.PIPE)
    print("finished :)")


if __name__ == "__main__":
    main()
