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

  # Step 1: Init
  queue = Queue()
  tw = TweetWorker(queue)
  cw = CouchdbWorker(queue, db_name=info_dict['dbname'])

  # Step 2: run TWITTER.API.SEARCH 这个好像只能一个keyword
  while True:
    print('running TweetWorker Search')
    search_flag = tw.run_search( info_dict['query'] )  # 0: normal return, 1: cannot find result 
    if search_flag == 1:
      break

    print('running CouchdbWorker')
    cw.run_save()
    time.sleep(10)
  
  # Step 3: run TWITTER.API.STREAM  这个可以list of keyword
  print('running TweetWorker Stream')
  tw.run_stream(info_dict['query'])  # Run Streamming Async in a new thread

  cw_save_failed_count = 0  # Retry 5 times. If meanwhile, nothing being put into queue, exit
  while True:
    if not queue.empty():
      cw.run_save()
      cw_save_failed_count = 0
    else:
      if cw_save_failed_count >= 5:
        sys.exit(0)

      cw_save_failed_count += 1
      print("Retry {}/5,".format(cw_save_failed_count))
      time.sleep(10)


