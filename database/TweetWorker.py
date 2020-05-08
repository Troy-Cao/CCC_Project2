
import tweepy
import datetime
import time
import json
import sys
from tweepy import OAuthHandler, API

class TweetWorker:
    # OAuth
    __consumer_key = "dL2ZAItvpFLiCULxa8Y7E5Utg"
    __consumer_secret = "hnLfXSmCTNSAJ2rsU9QOAvUFG159wysgGwy38sQyt0XKDte70M"
    __access_token = "709584127-zufPerRgSs4TDMscyfon47CIsN2AuXapBU8XEhty"
    __access_token_secret = "wzpAq42SKJP4XpqXqWAfiNsAJmXKjN2AQSeP51BvIETE2"    
    
    
    ####
    def __init__(self, queue):
        self.log('\n'*2 + "="*110)
        self.log("\n__Initialized__ @" + time.asctime(time.gmtime()) + "\n")
        self.log("="*110 + '\n'*2)
        auth = OAuthHandler(self.__consumer_key, self.__consumer_secret)
        auth.set_access_token(self.__access_token, self.__access_token_secret)
        self.api = API(auth)#, wait_on_rate_limit=True, wait_on_rate_limit_notify=True) 
            # TODO: test if auto waits and resumes
        
        self.last_min_id = None
        self.last_max_id = None
        self.request_count = 0  # For fun, keep track of number of requests.
        self.queue = queue
 
        self.isIDInit = False  # Flag for tweet id check
        self.round_count = 0  # Track the search round
      
    def log(self, message):
        """ Logs all operating message in to txt file.
            Only for Debugging use.
        """
        print(message)
        with open("log_tweetWorker.txt", "a") as f:
            f.write(message+'\n')
    
    def get_until_date(self, q, shift = 8):
        ''' Get the oldest possible tweet date from now.
                (Twitter standard -> 7-day-history -> can get tweets until 6 days ago)
                (In fact, can actually searched 8 days ago)
            Input: q = <'query_string'>
                   shift = <num of days before today>
            Return: The earliest date that API.search returns a result in "YYYY-MM-DD"
        '''
        today = datetime.date.today()
        
        while True:      
            shift_date = time.timedelta(days = shift) 
            until = (today - shift_date).strftime("%Y-%m-%d")
            
            self.request_count += 1
            self.log("[get_until_date] Request Count: "+str(self.request_count))
            
            if api.search(q = q, until = until, count = 1):
                print(until)
                return until
            shift -= 1
            
    def get_oldest_tweet_id(self, q):
        ''' Get the oldest possible tweet id for query q.
            (Twitter standard -> 7-day-history)
        '''        
        self.request_count += 1
        self.log("[get_oldest_tweet_id] Request Count: "+str(self.request_count))
        
        until = self.get_until_date(q)
        res = self.api.search(q = q, until = until)
        
        id = res[-1]._json['id']
        print("Oldest ID: ", id)
        return id
    
    def get_latest_tweet_id(self, q):
        ''' Get the latest possible tweet id for query q
        '''
        self.request_count += 1
        self.log("[get_latest_tweet_id] Request Count: "+str(self.request_count))
        
        # Will Retry, until get a tweet, or trial upto 10 times
        count = 0
        while count <= 10:
            count += 1
            self.log("[get_latest_tweet_id] Getting the latest ")
            try: 
                res = self.api.search(q = q)
                id = res[0]._json['id']
                return id
            except:
                print("Cannot find tweets... Retry in 10 sec")
                time.sleep(10)
                
        self.log("[get_latest_tweet_id] Cannot find tweets after 10 trials...")
        self.log("[get_latest_tweet_id] Exit system.")
        sys.exit(0)
        return None

    def search_tweets(self, q, lang="en", count=100):
        ''' 
        '''
        self.request_count += 1
        self.log("[search_tweets] Request Count: "+str(self.request_count))
        
        # API.search(q[, geocode][, lang][, locale][, result_type]
          # [count (max=100)][, until][, since_id][, max_id])
          # https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
        print("[search_tweets] Searching latest id: ", self.last_min_id)
        result_status = self.api.search(
                      q = q, 
                      count=100,
                      max_id = self.last_min_id,
                      result_type = 'recent',
                      lang = 'en' )
                      # geocode = "-37.827024, 144.955603, 45mi"  # Melbourne
        
        # Update last_min_id for next round of search as 'max_id'.
        self.last_min_id = result_status[-1]._json['id']
        
        
        return result_status  # can be empty, []
        
    def stream_tweets(self):
        # TODO: search玩，可以用stream继续搜
        return
    
    def rate_limit_handle(self, func, q):
        ''' Try to use API. Wait if rate limit reached. 
        '''
        try:
            ret = func(q=q)
            return ret

        # Catch Twitter API rate limit exception and wait for 15 minutes
        except tweepy.RateLimitError:
            print('Hit Twitter API rate limit.')
            for i in range(3, 0, -1):
                print("Wait for {} mins.".format(i * 5))
                time.sleep(5 * 60)
            print("Finished Waiting.")

        # Catch any other Twitter API exceptions
        except tweepy.error.TweepError:
            print('\nCaught TweepError exception')
    
    def check_end(self):
        ''' If run_search process reaches the earlies tweet it can get, return True.
                Then, stop run_search'''
        return

    def run_search(self, query):
        ''' This is the main run. 
                Continously search tweets in chronical order, and save every tweet
                (to Queue in which the elements will be popped into database)
            query: topic of interest 
        '''
        # Step 1: Init the latest tweet id for 'max_id' in api.search()
            # |=============================================================|
            # ^-7days ago                                                   ^-today
            #                                        |======================|
            #     current_min/last_min_4_next_search-^                      ^-max_id
            #                      |=================|
        
        if not self.isIDInit:
            self.last_max_id = self.get_latest_tweet_id(q=query)
            self.last_min_id = self.last_max_id
            self.log("[MAIN RUN] last_max_id: "+ str(self.last_max_id))
            self.isIDInit = True
            
            
        # Step 2: Search Tweet            
        self.log("[MAIN RUN] Current round: "+str(self.round_count))
        self.round_count += 1
        
        func = self.search_tweets
        result_status = self.rate_limit_handle(func, query)

        search_failed_count = 0
        if (not result_status) and (search_failed_count <= 5):  # Retry 5 times if search failed
            search_failed_count += 1
            self.log("[MAIN RUN] Failed to search tweets, retry {}/5".format(search_failed_count))
            time.sleep(30)
            func = self.search_tweets
            result_status = self.rate_limit_handle(func, query)
        elif (not result_status) and (search_failed_count > 5):
            return 1  # Flag (Cannot find result)
            
            
        # Step 3: Save the status
        result_count = 0  # Count the number of tweets in this search result
        
        if result_status:
            for status in result_status:
                self.log("On status #: "+str(result_count) + " of round #: "+str(self.round_count))
                
                result_count += 1
                
                status_json = status._json
                status_id = status_json['id']
                status_date = status_json['created_at']
                
                self.log("  |--id: "+str(status_id) + " |--date: "+ status_date)
                
                # Option1: save to json <- 弃用
#                     with open('json_cache/' + str(status_id) + '.json', 'w') as f:
#                         json.dump(status_json, f)
                # Option2: Save to queue
                self.queue.put(status_json)  

        return 0  # Flag (Result found)

    def run_stream(self, queue):
        

        return
