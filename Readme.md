# Nginprox

This project seeks to solve vulnerabilities caused by the upload of unwanted files to web application with the help of Nginx's reverse proxy feature.
A lot of modern web applications implement some variation of a file uploading system. Such systems can introduce vulnerabilities to the web application by having the user upload a file that will damage the server (a Web Shell) or a file that could be used to damage the users (an html file with scripts for example).


## Theory

Nginx's reverse proxy works by reading a configuration file with proxy rules and redirecting incoming requests to the address in the configuration file.
These rules are read from top to Bottom and the most specific rule is chosen.
So if
```
example.com/help/contact-us
```
is requested, and in the configuration contains the following rules:
```
location = /help/* {
  proxy_pass http://real.server.com/help/main-page;
     }
location = /help/contact-us {
  proxy_pass http://real.server.com/help/contact-us;
     }
```
The request will be directed to `http://real.server.com/help/contact-us`

Using this feature we can create a configuration file on a reverse proxy server that specifically points to every page on the original server. In order to allow users to access uploaded files we can implement a rule with whitelisted file extensions using regex. And send the rest to a generic "404" page.

Note: This only blocks access to the uploaded file, and not the upload itself.


## The Configuration File

Following the theory we create a configuration file with the following structure:
- Nginx Defaults (settings that need to be included in every Nginx configuration file).
- Specific proxy rules for every page on the original server
- Regex whitelist for allowed file extensions.
- A catch all to catch all unrecognized requests and redirect them to a "404" page.

## Current state

### This is a PoC

**This is by all means a Proof of Concept. Don't use this project to increase the security of your web application (it will probably break it).**

### Issues

If the theory is correct we potentially found an end to all web shells, right? well things are a bit more complicated then simple sites with URLs pointing to files on the server.

In the real world most web applications make use of rewrite rules to interact with dynamic pages. So the solution has to take that into account and potentially read  the web-server's config file and create proxy rules that match.


### Use Cases

In its current state Nginprox only works for _"simple"_ website that don't implement rewrite rules.

currently two use cases are supported:

1. Having a separate reverse proxy dedicated server.
2. Self "reverse proxy" where the original server will only be open to requests from and Nginx will redirect to localhost

#### Prerequisites

Nginprox is a **python 3** script  that creates the nginx.conf file that dictates the reverse proxy rules.

### help

```
usage: nginprox.py [-h] [-p PROXY] [-r ROOT_FOLDER] [-i]

optional arguments:
  -h, --help            show this help message and exit
  -p PROXY, --proxy PROXY IP to proxy to (e.g. "example.com" / "192.168.1.2" ) on default using localhost
  -r ROOT_FOLDER, --root-folder ROOT_FOLDER Specify the web-server's root directory (e.g /var/www/html), by default using current directory
  -i, --install         Use -i to install the Nginx and set it up with reverse proxy
```

### Use

1. Using Nginprox in order to create a .conf file to use with separate reverse proxy (as root in the original server):
```
python3 nginprox.py -r /var/www/html -p real.server.com
```
then take the created `nginx.conf` file and place it in the proxy server's `/etc/nginx/` folder. After that is done access to the web app would only be done through the proxy server and the original server would be set up to only accept requests from the proxy server.

2. Using Nginprox to set up a "self reverse proxy" (as root):
```
python3 nginprox.py -r /var/www/html -i
```
This will create the `nginx.conf` file, install the nginx service and place the conf file in `/etc/nginx/` </br>Note: this is will bind nginx to port 8888.


## TODO

- [ ] SSL support
- [ ] Logging
- [ ] Reading existing rewrite rules

## Powered By [Komodo Consulting](https://www.komodosec.com)
<p align="center">
  <img src="https://www.komodosec.com/wp-content/uploads/2016/05/komodologo.png" width=350/>
</p>
