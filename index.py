#!/usr/bin/env python2.7

import cgitb;

cgitb.enable() # Comment out to disable web tracebacks

import cgi
import re
import subprocess

from mako.template import Template

def main():
    query = cgi.FieldStorage()

    servers = {}

    if "server" not in query or "feature" not in query:
        # Define features here. Each tuple defines a
        # port@server and a tuple of feature names.
        licenses = [
            ('12345@server-name', ('feature-1', 'feature-2')),
            ('23456@server-name', ('feature-3', 'feature-4')),
        ]
    else:
        server = query.getvalue("server")
        feature = query.getvalue("feature")

        licenses = [(server, (feature,))]

    for server, features in licenses:
        servers[server] = {}

        for feature in features:
            servers[server][feature] = get_licenses(server, feature)

    template = Template(filename='flexlm.html', module_directory='cache')

    print 'Content-Type: text/html'
    print

    print template.render(data=servers)

def get_licenses(server, feature):
    licenses = []

    try:
        output = subprocess.check_output(["./lmutil", "lmstat", "-c", server,
            "-f", feature])
    except subprocess.CalledProcessError:
        return licenses

    for line in output.splitlines(True):
        if "start" in line:
            license = line.strip()

            license_re = re.compile(r"""(?P<user>[^\s]+)\ 
                    (?P<computer>[^\s]+)\ 
                    (?P<computer2>[^\s]+)\ 
                    \((?P<version>[^\s]+)\)\ 
                    \((?P<connection>[^,]+)\),\ 
                    start (?P<start>.+)""", re.X)

            licenses.append(license_re.match(license).groupdict())

    return licenses

if __name__ == "__main__":
    main()
