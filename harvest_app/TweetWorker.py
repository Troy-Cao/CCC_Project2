
import tweepy
import datetime
import time
import json
import sys
from tweepy import OAuthHandler, API, Stream, StreamListener

def generate_grid_coord_list(top_left_coord, height, width, diameter):
    """ Magic function to generate a list of coordinates for searching tweets.
        The density is the 2 * min distance between two coordinates.
        It's like a pile of orange, in 2-D
                                             0 0 0 0 0 
                                            O O O O O
                                             0 0 0 0 0
                                            O O O O O
        height: [km]
        width: [km]
        diameter: [km]
    """
    import math, random
    def km_2_lat():
        return 111.32
    def km_2_long(Alat, Along):
        circ = 40075     # km - earch circumference
        return circ * math.cos(math.radians(Alat)) / 360
    
    result = []
    
    # Init
    radius = diameter / 2
    h_per_layer = radius * math.sqrt(2)
    init_lat = top_left_coord[0]
    init_long = top_left_coord[1]
    
    # Calculate
    lat_index = km_2_lat()
    
    for h in range(int(height/h_per_layer) + 1):
        long_index = km_2_long(init_lat, init_long)
        lat = init_lat - h * h_per_layer/lat_index
        
        # 错层的话，x位置不一样
        if h % 2 == 0:  
            tmp_init_long = init_long
        else:
            tmp_init_long = init_long + radius/long_index
        
        for w in range(int(width/diameter) + 1):
            
            long = tmp_init_long  + w * diameter/long_index
            lat_noise = random.randint(0,1000)/500000  - 1000/500000
            long_noise = random.randint(0,1000)/500000  - 1000/500000
            if random.randint(0, 10) > 5:
                lat_noise /= 10
            if random.randint(0, 10) > 5:
                long_noise /= 10
                
            result.append( [round(lat+lat_noise, 8), round(long+long_noise, 8)] )
    
    return result


class MyStreamListener(StreamListener):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        
    def on_status(self, status):
        print("Status ID = ",status._json['id'])
        print(status.text, '\n')
        status_json = status._json
        status_json = self.handle_coord(status_json)
        self.queue.put(status_json)
        
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

        # returning non-False reconnects the stream, with backoff.

    

class TweetWorker:
    # OAuth
    __consumer_key = "dL2ZAItvpFLiCULxa8Y7E5Utg"
    __consumer_secret = "hnLfXSmCTNSAJ2rsU9QOAvUFG159wysgGwy38sQyt0XKDte70M"
    __access_token = "709584127-zufPerRgSs4TDMscyfon47CIsN2AuXapBU8XEhty"
    __access_token_secret = "wzpAq42SKJP4XpqXqWAfiNsAJmXKjN2AQSeP51BvIETE2"    
    
    
    ####
    def __init__(self, queue, info_dict):
        self.log('\n'*2 + "="*110)
        self.log("\n__Initialized__ @" + time.asctime(time.gmtime()) + "\n")
        self.log("="*110 + '\n'*2)
        self.auth = OAuthHandler(self.__consumer_key, self.__consumer_secret)
        self.auth.set_access_token(self.__access_token, self.__access_token_secret)
        self.api = API(self.auth)#, wait_on_rate_limit=True, wait_on_rate_limit_notify=True) 
            # TODO: test if auto waits and resumes
        
        # Argument-related. Contains all the query, location, etc information
        self.info_dict = info_dict

        # Twitter API related
        self.last_min_id = None
        self.last_max_id = None
        self.request_count = 0  # For fun, keep track of number of requests.
        self.queue = queue
 
        self.isIDInit = False  # Flag for tweet id check
        self.round_count = 0  # Track the search round

        # Coordinates Handler
        self.grid = generate_grid_coord_list((-37.662298, 144.730412), 40, 50, 1)
      

    def log(self, message):
        """ Logs all operating message in to .out file.
            Only for Debugging use.
        """
        print(message)
        with open("log_tweetWorker.out", "a") as f:
            f.write(message+'\n')
    

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
                      geocode = self.info_dict['coord_location'],
                      lang = 'en' )
                      
        
        # Update value (last_min_id - 1) for next round of search as 'max_id'.
        if result_status:
            self.last_min_id = result_status[-1]._json['id'] - 1 
        
        return result_status  # can be empty, []
        
    
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
    

    def handle_coord(self, Tjson):
        ''' Handle coordinates'''
        import random
        if not Tjson["coordinates"]:
            if random.randint(0,100) < 10:
                addIn = { "type": "Point", "coordinates": self.grid[random.randint(0, len(self.grid)-1)] }
                Tjson["coordinates"] = addIn
        return Tjson


    #####################################################################################

    def reset_search(self):
        """ Reset isIDInit for the next query word. 
        """
        self.isIDInit = False
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
        result_status = self.rate_limit_handle(func, query)  # Rate limit control

        # Retry 5 times if single search fails; Raise error flag=1 when all 5 searchs fail.
        search_failed_count = 0  
        while not result_status:
            search_failed_count += 1
            if (search_failed_count <= 5):  
                self.log("[MAIN RUN] Failed to search tweets, retry {}/5".format(search_failed_count))
                time.sleep(10)
                func = self.search_tweets
                result_status = self.rate_limit_handle(func, query)
            else:
                return 1  # Flag (Cannot find result)
            
        # Step 3: Save the status
        result_count = 0  # Count the number of tweets in this search result
        
        if result_status:
            for status in result_status:
                result_count += 1
                
                status_json = status._json # json file (as a python dict)
                status_json = self.handle_coord(status_json)

                status_id = status_json['id']
                status_date = status_json['created_at']
                self.log("Searching: "+query+". On tweet #: "+str(result_count) + " of round #: "+str(self.round_count)
                        + " |--id: "+str(status_id) + " |--date: "+ status_date[4:19])
                
                # Option1: Save to queue
                self.queue.put(status_json)

        return 0  # Flag (Result found)


    def run_stream(self):
        myStreamListener = MyStreamListener(self.queue)
        myStream = Stream(auth=self.auth, listener=myStreamListener)
        
        locations = self.info_dict['box_location']
        track = self.info_dict['query']

        myStream.filter(track=track, languages=['en'], is_async=True, locations=locations)
        return
