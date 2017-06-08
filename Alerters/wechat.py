try:
    import requests
    requests_available = True
except:
    requests_available = False

from alerter import Alerter

try:
    from wechatpy.client import WeChatClient
    wechat_available = True
except:
    wechat_available = False

try:
    from wechatpy.session.redisstorage import RedisStorage
    from redis import Redis
    redis_available = True
except:
    redis_available = False


class WechatAlerter(Alerter):
    """Send alerts to a Wechat message.
    Subscription required, see https://mp.weixin.qq.com/wiki"""

    access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
    mass_send_url = 'https://api.weixin.qq.com/cgi-bin/message/mass/send?access_token=%s'

    def __init__(self, config_options):
        if not requests_available:
            print "Requests package is not available, cannot use SlackAlerter."
            return

        Alerter.__init__(self, config_options)
        try:
            appid = config_options['appid']
            secret = config_options['secret']
            template = config_options['template']
            users = config_options['users']
            redis = config_options['redis']
        except:
            raise RuntimeError("Required configuration fields missing")

        if appid == "" :
            raise RuntimeError("missing wechat appid")

        if secret == "" :
            raise RuntimeError("missing wechat secret")

        if template == "" :
            raise RuntimeError("missing wechat secret")

        if users == "" :
            raise RuntimeError("missing users secret")

        self.appid = appid
        self.secret = secret
        self.template = template
        self.users = users
        self.redis = redis

    def send_alert(self, name, monitor):
        """Send the message."""

        type = self.should_alert(monitor)
        message_json = {}
        message_json['first'] = {'value': 'please note', 'color': '#173177'}
        message_json['keyword1'] = {'value': 'monitor status changed!', 'color': '#173177'}
        message_json['keyword2'] = {'value': monitor.describe(), 'color': '#173177'}
        message_json['remark'] = {'value': 'please deal with it in time', 'color': '#173177'}
        if type == "":
            return
        elif type == "failure":
            message_json['first'] = {'value': 'WARNING : monitor[{}] failed, on host[{}] , at {}!'.format(name, self.hostname, self.format_datetime(monitor.first_failure_time())), 'color': '#ff0000'}
            message_json['keyword3'] = {'value': monitor.get_result(), 'color': '#ff9900'}
            try:
                if monitor.recover_info != "":
                    message_json['remark'] = {'value': '{}'.format(monitor.recover_info), 'color': '#000000'}
            except AttributeError:
                pass
        elif type == "success":
            message_json['first'] = {'value': 'CONGRATULATION : monitor[{}] succeeded, on host[{}] , first failed at {}!'.format(name, self.hostname, self.format_datetime(monitor.first_failure_time())), 'color': '#00ff00'}

        else:
            print "Unknown alert type %s" % type
            return
        if not self.dry_run:
            try:
                r = self.send_wechat_template(message_json)
                if not r['errcode'] == 0:
                    print "POST to wechat message failed"
                    print r
            except Exception, e:
                print "Failed to post to wechat message"
                print e
                print message_json
                self.available = False
        else:
            print "dry_run: would send wechat: %s" % message_json.__repr__()

    def send_wechat_template(self, data):
        """ template
        {{first.DATA}}
        title1:{{keyword1.DATA}}
        title2:{{keyword2.DATA}}
        title3:{{keyword3.DATA}}
        {{remark.DATA}}
        """
        if not wechat_available:
            result_json = {"errcode": 40002}
            return result_json

        if redis_available and self.redis != "":
            redis_client = Redis.from_url(self.redis)
            session_interface = RedisStorage(redis_client,prefix="wechatpy")
            wechat_client = WeChatClient(self.appid,self.secret,session=session_interface)
        else:
            wechat_client = WeChatClient(self.appid,self.secret)
        for user in self.users.split(","):
            result_json = wechat_client.message.send_template(user,self.template,data)
        return result_json
