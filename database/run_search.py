import time
from TweetWorker import TweetWorker
from CouchdbWorker import CouchdbWorker
from queue import Queue 
import sys, getopt

class Manager:
  def __init__(self, q):
    pass


def parse_arg(argv, info_dict):


  return


if __name__ == "__main__":
  ''' Process will extract twitter json and save to db '''
  # Step 0: Preparation for query
  info_dict = {}
  parse_arg(sys.argv[1:], info_dict)

  info_dict['dbname'] = "tweet_json_1"
  info_dict['query'] = "stayhome"

  

 

  # 
  queue = Queue()
  tw = TweetWorker(queue)
  cw = CouchdbWorker(queue, db_name=info_dict['dbname'])

  # TWITTER.API.SEARCH
  while True:
    print('running TweetWorker')
    search_flag = tw.run_search( info_dict['query'] )  # 0: normal return, 1: cannot find result 
    if search_flag == 1:
      break

    print('running CouchdbWorker')
    cw.run_save()

    time.sleep(10)
  
  # TWITTER.API.STREAM



