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
