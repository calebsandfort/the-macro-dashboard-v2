Notes
- This was designed for my personal use to better visualize MyFractalRanges ranges and bring together other variables that I like to look at when 
  making a trade, as well as managing my overall portfolio. It sources price data from TD Ameritrade because it is free and real time.
  You could swap out ranges and data if you wanted.
- The data does not update as the app is running, although that is something that could be added.
- The crowding data is free-ish. Due to that fact, it is not available for every ticker.
    - An explanation of how to interpret the crowding chart can be found at the bottom of this page: https://42macro.com/faq/
    - I include the last 10 days so you can get a feel for the movement of the asset. The larger/bluer the dot, the more recent.

Data - https://developer.tdameritrade.com/content/simple-auth-local-apps

The app uses the TD Ameritrade API for real time data. You must have a TD Ameritrade account to get the data. If you do not have one,
you can always open an account and not fund it. Or adapt the code to your preferred data provider.

1. Go to https://developer.tdameritrade.com/ and register.
2. Read https://developer.tdameritrade.com/content/getting-started to familiarize yourself with TD Ameritrade API
3. Register an app. Set callback URL to "https://127.0.0.1"
    a. Make note of your Consumer Key on the Keys tab for the app
4. Replace consumer key in this url and hit it in a browser: https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1&client_id=<Consumer Key>%40AMER.OAUTHAP
5. You will get a url in the browser address bar like this: https://127.0.0.1/?code=i03mYbZrlxm%2BxPErooovCOA%2FKwot5fIQd8If5GpVaWKZ5wUkcbr%2FAQMobltg749SI5lguD3qBrOgZJbFv2lXDsmCDSiYATBPwdHCWCfVd2RiOJAcG0nVwgY6X%2BWkLSE%2B4%2FII06nSMmfCYxB1jj3P3u4M2Bzgs%2FG4J2C2knQoiOJ98wPhafUwBVkGG1yzk3cqTyCk%2Bn%2B%2Fe1OLP3VPenpojqOu%2FyZqdar9qLgLcfuA6%2Bp1uFwnigaKMMhCdsKNrFuWbBgWyury3GkR8I%2FkaApLMHJJLTKtJFQGMhAlL0vPYtZLsMEVfNHmAw1MFGFHxs8orC8sxN06%2F39jBr3crfjiKyyxrK4i7nhoxAifCRZzbT337br3RoztiMYd9BENTrUpB%2B3e7LK9qpSIMWPa%2FgklVCzmILBvZ243%2FClBOxX4FNu1n1YppLteVaiUalp100MQuG4LYrgoVi%2FJHHvlS%2BrcXeemIibX1B9liCtwHTYAIuk72flyvmmnAa%2FOdiY98DmMyYm8KT2DPFPrTAbq%2BSPaaefWb4iYkPSOSrdzoW%2BKn7j%2FuRJfTyhkNSay4hG8jrQon%2B4ZJxSeH1Rlbiapl63XW4h7cGnik7ZMjeV0pLUGCWGhtV%2FsHkntEr1707iWmaCQ87%2BzGxvGXL%2FzxcatIJzjMQNQeiTLASf7tRxGy60PLiQFpp5K8v%2FGyQ1wEf8BqVfBjapxTY3CJTpfVbPUcIbjey2TubkaLjK6MG6qMeaf2zdC0WJcP33tsDUnc%2FK%2BKUOmh%2FSOMDWKTLqD00D48jEc5v4lscnNLJKH60SXOgQDSV%2Fanqzt5g%2BN0DuldzOM3OuvuH2P4AJvT0OIUZesffxtXpEDFnsaYqr7JcPosHeG6aVsTj8%2FpH0FyeZQ7p5zyC8yS%2BPW8jQHgg8%3D212FD3x19z9sWBHDJACbC00B75E
6. Copy everything after code=
7. Go to https://www.urldecoder.org/ and decode the text
8. Go to https://developer.tdameritrade.com/authentication/apis/post/token-0 and follow steps 3-5 from here https://developer.tdameritrade.com/content/simple-auth-local-apps
9. If all done correctly you will see a successful HTTP 200 response below.
10. In the python project rename apiKeys.sample.py to apiKeys.py and paste your consumer key and refresh token from the steps above in the appropriate places.
11. You should now have free access to real time data. This process will need to be repeated every three months, as the refresh token will expire.

Environment and Codez
1. Download and install Anaconda: https://www.anaconda.com/
2. Download and unzip project from github: https://github.com/calebsandfort/the-macro-dashboard-v2
3. Open an Anaconda Prompt
    a. Navigate to project folder: cd "<path to folder>"
    b. Run command "pip install -r requirements.txt" to install necessary packages
    
Daily Maintenance
1. Download your portfolio csv from MyFractalRanges into the mfr folder with the filename format of yyyy-mm-dd.csv
2. Construct a Portfolio.csv in the portfolios folder in the same manner as Portfolio.Sample.csv
3. Update Potentials.csv with tickers you want to keep an eye on.

Usage
1. Open an Anaconda Prompt
    a. Navigate to project folder: cd "<path to folder>"
    b. Run command "python macroDashboardMfr.py" to run project ****You'll want to do step 2a the first time you rune the project
    c. Once command prompt prints "done" hit "http://127.0.0.1:5435/"
    d. Clicking a ticker will pop open the info dialog for the corresponding asset.
2. Optional flags
    a. "-r" => this will download up to date data for your tickers => "python macroDashboardMfr.py -r"
    b. "-d" => this will run the project in debug mode. Useful if you are coding => "python macroDashboardMfr.py -d"
    
    
Useful links
- https://dash-bootstrap-components.opensource.faculty.ai/docs/
- https://plotly.com/python/reference/
- https://plotly.com/python/
- https://www.anaconda.com/
- https://dash.plotly.com/