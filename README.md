[![Build Status](https://travis-ci.org/jamesoff/simplemonitor.svg?branch=master)](https://travis-ci.org/jamesoff/simplemonitor)

SimpleMonitor is a Python script which monitors hosts and network connectivity. It is designed to be quick and easy to set up and lacks complex features that can make things like Nagios, OpenNMS and Zenoss overkill for a small business or home network. Remote monitor instances can send their results back to a central location.

Documentation is here:
http://jamesoff.github.io/simplemonitor/

wechat configure section in monitor.ini
[wechat]
type=wechat
appid=appid1234567890
secret=secret1234567890
template=templateid1234567890
users=openid1,openid2
redis=redis://[:password]@host:port/database
