#!/usr/bin/python
import ast
import sys
import urllib
import optparse
import datetime

verbose = False

def parse(url, tree=None):
  if url[-1] != "/":
    url += "/"
  url = "%sapi/python" % url
  if tree:
    url += "?tree=%s" % tree
  return ast.literal_eval(urllib.urlopen(url).read())

def find_committers(url):
  jobs_in_view = parse(url, "jobs[name,url]")['jobs']

  print "Yellow committers:"

  culprits = []
  culprit_ids = {}
  days = {}
  for job in jobs_in_view:
    print_if_verbose('Querying %s...' % job['name'])
    builds = parse(job['url'], "builds[result,timestamp,culprits[id,fullName]]")

    for build in builds['builds']:
      result = build['result']
      print_if_verbose("  " + result)
      if result != 'SUCCESS':
        if culprits:
          print_if_verbose("  Adding:")
          for culprit in culprits:
            print_if_verbose("    " + culprit['id'])
            culprit_ids[culprit['id']] = culprit['fullName']
        culprits = build['culprits']
      else:
        if culprits:
          print_if_verbose("  Removing:")
          for culprit in culprits:
            culprit_id = culprit['id']
            print_if_verbose("    " + culprit_id)
            if culprit_id in culprit_ids:
              del culprit_ids[culprit_id]
        culprits = []
        if culprit_ids:
          date = get_date(build)
          print date
          for id in culprit_ids:
            print "  " + id + ", " + culprit_ids[id]
          days[date] = culprit_ids
        culprit_ids = {}

def get_date(build):
  return datetime.date.fromtimestamp(int(build["timestamp"])/1000)

def print_if_verbose(message):
  if verbose:
    print message

def main():
  global verbose
  parser = optparse.OptionParser(usage="""Usage: %prog VIEW_URL [options]

Gets yellow committers for all jobs in the supplied Jenkins view.""")
  parser.add_option("-v", "--verbose", action="store_true", default=False,
    help="Prints progress, instead of only the revision")
  parser.add_option("-d", "--debug", action="store_true", default=False,
    help="Prints stack traces")
  try:
    (options, (url,)) = parser.parse_args()
    verbose = options.verbose
    find_committers(url)
  except ValueError, e:
    if options.debug:
      raise e
    parser.print_help()
    return 1

if __name__ == '__main__':
	sys.exit(main())