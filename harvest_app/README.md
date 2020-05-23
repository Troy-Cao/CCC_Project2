## 23/05/2020 - Updates
The harvester can now fill in the coordinates value according to the GEOCODE provided during search.


## 12/05/2020 - Updates

### 1. Code Updates
1. Renamed `run_search.py` to `run_harvest.py`
2. The `run_harvest.py` now handles command line arguments.
3. The `run_harvest.py` now accepts a list of keyword for query. *e.g [stayhome, quarantine].*  The harvest logic follows: <br>
  - After exhausting api.search on keyword1, exhaust api.search on keyword2, up until the last keyword N. <br>
  - After that api.stream will run simultaneously on all key words.


##### More on 2 - (The run_search.py now handles arguments)
```shell
usage: Run-Harvest [-h] -q QUERY [QUERY ...] [-l LOCATION] [-lr RADIUS]
                   [-db DATABASE]

description: Reads command and parse argument for running harvert app.

optional arguments:
  -h, --help            show this help message and exit
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        A list of keyword you want to find tweets about.
  -l LOCATION, --location LOCATION
                        default='Melbourne'. City/Country name. If coordinate
                        of the location cannot be found, will use default
                        value.
  -lr RADIUS, --location_radius RADIUS
                        Radius around the location coordinate intersted.
  -db DATABASE, --db_name DATABASE
                        default='Default_Tweets'
```

Example call:

```shell
$ python run_harvest.py -q stayhome quarantine social-distance lockdown coronavirus covid-19 self-isolate -lr 100mi -l Sydney
```
### 2. Database Updates
The following list of keywords are being filtered and saved into database with name "Default_Tweets" @172.26.130.241:5984. <br>
`[stayhome quarantine social-distance lockdown coronavirus covid-19 self-isolate]`

Other parameters are:
- location="Melbourne"
- radius="50mi"


---

## 08/05/2020 -
- Terminal里面 `$python database/run_search.py` 应该就能search和stream关于’stayhome'的推特了。
- search的地理位置限制在墨尔本
- stream不太容易限制地理位置

主要文件就是
1. run_search.py
2. CouchdbWorker.py
3. TweetWorker.py

\*存进database的数据 id和id_str有区别。用id_str。

*Note: 'status' and 'tweet' are used intervchangably in \*.py files*

---
### [Tweet Object](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json)

### [Rules and filtering - Building standard queries](https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators)

The best way to build a standard query and test if it’s valid and will return matched Tweets is to first try it at twitter.com/search. As you get a satisfactory result set, the URL loaded in the browser will contain the proper query syntax that can be reused in the standard search API endpoint. Here’s an example:
1. We want to search for Tweets referencing @TwitterDev account. First, we run the search on twitter.com/search
2. Check and copy the URL loaded. In this case, we got: https://twitter.com/search?q=%40twitterdev
3. Replace https://twitter.com/search with https://api.twitter.com/1.1/search/tweets.json and you will get: https://api.twitter.com/1.1/search/tweets.json?q=%40twitterdev
4. Run a Twurl command to execute the search.

e.g.
- movie -scary :)	containing “movie”, but not “scary”, and with a positive attitude.
- traffic ?	containing “traffic” and asking a question.
- puppy filter:media	containing “puppy” and an image or video.

### [Filtering Tweets by location](https://developer.twitter.com/en/docs/tutorials/filtering-tweets-by-location)
flight :(	containing “flight” and with a negative attitude.
