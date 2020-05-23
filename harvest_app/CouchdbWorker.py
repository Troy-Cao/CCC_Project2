import couchdb
import time

class CouchdbWorker:
    """ save json documents to db "tweet_json"
    """
    __user = "admin"
    __secret = "admin"
    
    
    
    def __init__(self, queue, info_dict):
        """ queue: TweetWorker PUT status to queue, CouchdbWorker GET and save to db
        """
        login = self.__user + ':' + self.__secret
        route = "@172.26.130.241:5984/"
        url = "http://" + login + route
        
        self.couch = couchdb.Server(url)
        db_name=info_dict['database']
        self.db = self.setup_db(db_name)
        self.queue = queue
        self.save_count = 0  # count the number of success SAVE to db
        
    def log(self, message): 
        """ Logs all operating message in to .out file.
            Only for Debugging use.
        """
        print(message)
        with open("log_couchWorker.out", "a") as f:
            f.write(message+'\n')
        
    def setup_db(self, name):
        ''' If db with <name> not exist, create one.
        '''
        try:
            db = self.couch[name]
        except couchdb.ResourceNotFound as e:
            self.log("Database " + name + " is not found. Creating one instead.")
            db = self.couch.create(name)
        except:
            self.log("Some Error??")
            db = self.couch.create(name)
        return db
    
    def save_doc(self, db, status_dict):
        ''' Save a dictionary object into database.
            Return <document id>, <document rev> if succeeded.
        '''
        try:
            status_id = status_dict['id_str']
            status_dict['_id'] = status_id
            tmp_id, tmp_rev = db.save(status_dict)
            self.save_count += 1
            self.log("Successful save: "+ str(self.save_count))
            return tmp_id, tmp_rev
        
        except couchdb.ResourceConflict as e:
            self.log("Database already have document: " + str(status_id))
        except :
            self.log("Unknown Error.")
    
        return None, None
    

    def run_save(self): # <<<---- 这个是两种 Worker 轮流跑的版本
        """ Continuously running to save doc from Queue() to db, until Queue() is empty
        """
        
        while True:
            if not self.queue.empty():
                doc = self.queue.get()
                self.save_doc(self.db, doc)
                continue
            return

  # def run_save(self): # <<<-------- 这个是continuous running版本
    #     """ Continuously running to save doc to db"""
        
    #     # IF queue is still empty after waiting for 5*15 mins, exit
    #     count = 0
    #     while count < 5:
    #         count += 1
    #         if not self.queue.empty():
    #             count = 0
    #             print("Not empty,", end=' ')
    #             doc = self.queue.get()
    #             self.save_doc(self.db, doc)
    #             continue
                
    #         # IF queue is empty, TwitterAPI may have reached rate limit, pause 15min
    #         self.log("."*40 + "waiting for TweetWorker..")
    #         time.sleep(15 * 60)
    