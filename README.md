# Overview
py-arvhiver archives and uploads logs to Box folder.

# Requirements

* python3 ( >= 3.8)

* python-dotenv [https://pypi.org/project/python-dotenv/](https://pypi.org/project/python-dotenv/)

* MonthDelta [https://pypi.org/project/MonthDelta/](https://pypi.org/project/MonthDelta/)

* Box Python SDK [https://github.com/box/box-python-sdk](https://github.com/box/box-python-sdk)

* python-slack-sdk [https://github.com/slackapi/python-slack-sdk](https://github.com/slackapi/python-slack-sdk)

# Support
Linux

# Usage
```
Usage: python3 py-archiver.py -m <month> -c <config>
```

# Install and Execute
```
git clone
cd py-archiver
mv sample.env .env
vi .env
 - enter your Box folder_id BOX_FOLDER_ID
python3 py-archiver.py -m YYYY-MM -c /path/to/your/config
```

