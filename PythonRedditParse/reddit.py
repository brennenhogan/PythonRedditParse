#!/usr/bin/env python3

import os
import sys
import requests
import pprint

# Globals

URL      = None
ISGD_URL = 'http://is.gd/create.php'
shorten = False
limit = 10
orderby = 'score'
titlelen = 60

# Functions

def usage(status=0):
    ''' Display usage information and exit with specified status '''
    print('''Usage: {} [options] URL_OR_SUBREDDIT

    -s          Shorten URLs using (default: False)
    -n LIMIT    Number of articles to display (default: 10)
    -o ORDERBY  Field to sort articles by (default: score)
    -t TITLELEN Truncate title to specified length (default: 60)
    '''.format(os.path.basename(sys.argv[0])))
    sys.exit(status)

def load_reddit_data(url=URL):
    ''' Load reddit data from specified URL into dictionary '''
    headers  = {'user-agent': 'reddit-{}'.format(os.environ.get('USER', 'cse-20289-sp19'))} #Prevents request errors
    r = requests.get(url, headers=headers)
    data = r.json()
    return data #Returns the full json file

def dump_reddit_data(data, limit=10, orderby='score', titlelen=60, shorten=False):
    ''' Dump reddit data based on specified attributes '''

    children = data['data']['children']

    if orderby == 'score':
        children = sorted(children, key = lambda c: c['data'][orderby], reverse=True) #Soring by score needs to be reversed
    else:
        children = sorted(children, key = lambda c: c['data'][orderby], reverse=False)

    for index, child in enumerate(children[:limit],1):
        title = child['data']['title']
        score = child['data']['score']
        url = child['data']['url']

        if shorten: #Calls upon the shorten function
            url = shorten_url(url)

        if index > 1:
            print() #Prints a blank line before all lines besides the first
        print('{:4}.\t{} (Score: {})'.format(index,title[:titlelen],score))
        print('\t{}'.format(url))


def shorten_url(url=URL):
    ''' Shorten URL using yld.me '''
    r = requests.get(ISGD_URL, params={'format': 'json', 'url':url})
    short = r.json()
    return short['shorturl']

# Parse Command-line Options

args = sys.argv[1:]
while len(args) and args[0].startswith('-') and len(args[0]) > 1:
    arg = args.pop(0)
    if arg == '-s':
        shorten = True
    elif arg == '-n':
        arg = args.pop(0)
        limit = int(arg)
    elif arg == '-o':
        arg = args.pop(0)
        orderby = arg
    elif arg == '-t':
        arg = args.pop(0)
        titlelen = int(arg)
    elif arg == '-h':
        usage(0)
    else:
        usage(1)

if len(args) and args[0].startswith('http') and len(args[0]) > 1: #If given a link
    URL = args.pop(0)
elif len(args)  and len(args[0]) > 1: #If given a subreddit name
    sub = args.pop(0)
    base = 'https://www.reddit.com/r/'
    URL = base+sub+'/.json'
else: #If given nothing, exit with a code of 1
    usage(1)


# Main Execution

data = load_reddit_data(URL)
dump_reddit_data(data, limit, orderby, titlelen, shorten)
