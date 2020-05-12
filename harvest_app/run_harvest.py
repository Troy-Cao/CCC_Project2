import time
from TweetWorker import TweetWorker
from CouchdbWorker import CouchdbWorker
from queue import Queue 
import sys, getopt
import argparse
# import geopy

class Manager:
  def __init__(self, q):
    pass


def parse_arg(info_dict):
  """ $ python run_harvest.py -q stayhome quarantine social-distance lockdown coronavirus covid-19 self-isolate
        -lr 100mi -l Sydney 
  """
  _query = ['covid-19', 'quarantine', 'stayhome', 'social-distance', 'lockdown', 'coronavirus', 'self-isolate']
  _cordinate = {'Melbourne': '-37.8142176,144.9631608',  # (location.latitude, location.longitude)
               'Sydney': '-33.8548157,151.2164539',
               'Australia': '-25.909836,134.470656'}
  _location_box = {'Melbourne': [ 143.990289, -38.507844, 145.539724, -37.508239 ],  # Melbourne
                   'Sydney'   : [ 150.496611, -34.100751, 151.341185, -33.576045 ],  # Sydney
                   'Australia': [ 113.554978, -37.908176, 153.534874, -12.317801 ]}  # Australia

  # The Parser:
  parser = argparse.ArgumentParser(description="description: Reads command and parse argument for running harvert app.",
                                    prog="Run-Harvest")

  parser.add_argument('-q', '--query', action='store', dest='query', required=True,
                          help = "A list of keyword you want to find tweets about.", nargs='+')
  parser.add_argument('-l', '--location', dest='location',  default='Melbourne',
                          help = "default=\'Melbourne\'. City/Country name. \
                          If coordinate of the location cannot be found, will use default value.")
  parser.add_argument('-lr', '--location_radius', action='store', dest='radius', default='50mi', 
                          help="Radius around the location coordinate intersted.")
  parser.add_argument('-db', '--db_name', action='store', dest='database', default='Default_Tweets',
                          help="default=\'Default_Tweets\'")

  ns = parser.parse_args()  # A Namespace object

  # Format and Save to info_dict for later use
  info_dict['database'] = str.lower(ns.database)  # couchDB only takes lower case
  info_dict['radius'] = ns.radius
  info_dict['query'] = ns.query
  if ns.location in _cordinate:
    info_dict['coord_location'] = _cordinate[ ns.location ] + ',' + ns.radius  # For Searching
    info_dict['location'] = ns.location
    info_dict['box_location'] = _location_box[ ns.location ]
  else:
    info_dict['coord_location'] = _cordinate['Melbourne'] +',' + ns.radius
    info_dict['location'] = 'Melbourne'
    info_dict['box_location'] = _location_box[ 'Melbourne' ]

 # TODO: Check Radius Format
  return ns


###############################################################################################
if __name__ == "__main__":

  ''' Process will extract twitter json and save to db '''
  # Step 0: Preparation for query
  info_dict = {}
  parse_arg(info_dict)
  print(info_dict)

  # Step 1: Init
  queue = Queue()
  tw = TweetWorker(queue, info_dict)
  cw = CouchdbWorker(queue, info_dict)

  # Step 2: run TWITTER.API.SEARCH 这个好像只能一个keyword
  for q in info_dict['query']:
    print(q)

    while True:
      print("="*80, '\n    running TweetWorker Search on key: ', q,'\n',"="*80)
      search_flag = tw.run_search(q)  # 0: normal return, 1: cannot find result 
      if search_flag == 1:  # meaning: had retried 5 times, and still cannot search new tweets
        tw.reset_search()
        break

      print("="*80, '\n    running CouchWorker\n',"="*80)
      cw.run_save()
      time.sleep(10)
  
  # Step 3: run TWITTER.API.STREAM  这个可以list of keyword
  print("="*80, '\n    running TweetWorker Stream on: ', info_dict['query'],'\n',"="*80)
  tw.run_stream()  # Run Streamming Async in a new thread
  time.sleep(10)

  cw_save_failed_count = 0  # Retry 5 times. If meanwhile, nothing being put into queue, exit
  while True:
    if not queue.empty():
      cw.run_save()
      cw_save_failed_count = 0
    else:
      if cw_save_failed_count >= 5:
        sys.exit(0)

      cw_save_failed_count += 1
      print("Queue is empty from streaming. Retry {}/5,".format(cw_save_failed_count))
      time.sleep(10)


