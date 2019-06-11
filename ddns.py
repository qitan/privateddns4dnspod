#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Charles
# Time:   20190601
# Desc:   Dnspod Record for own DDNS


import apicn
from ddns_config import BASEDIR, DNSPOD, IP_RECORD, SLEEP_TIME, LOG_LEVEL, LOG_PATH

import urllib2
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import os

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
logfile = os.path.join(LOG_PATH, 'ddns.log')
handler = TimedRotatingFileHandler(logfile,
                                   when='d',
                                   interval=1,
                                   backupCount=14)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    # please refer to:
    # https://support.dnspod.cn/Kb/showarticle/tsid/227/
    login_token = '{},{}'.format(DNSPOD['id'], DNSPOD['token'])

    ##domain = DNSPOD['domain']
    ##print "DomainList"
    ##api = apicn.DomainList(login_token=login_token)
    ##ret = api().get("domains")

    ##domain_id = ret[0]['id']
    ##print "%s's id is %s" % (domain.replace(DNSPOD['sub_domain']+'.', ''), domain_id)

    while True:
        time.sleep(SLEEP_TIME)
        try:
            res = urllib2.urlopen('http://ip.3322.net', timeout=10)
            value_new = res.read().strip('\n')
            print "New value is %s" % value_new
        except Exception, e:
            print "Query public ip address failed."
            print str(e)
            logger.error(str(e))
            continue
        try:
            print "Get ip record"
            with open(IP_RECORD, 'r') as f:
                value_old = f.read()
        except:
            print "Create ip record file"
            with open(IP_RECORD, 'w') as f:
                f.write(value_new)
            value_old = value_new

        if value_new == value_old:
            err_msg = "Value %s not change, do not need to modify record" % value_new
            print err_msg
            logger.error(err_msg)
            continue
        print "Update value"
        with open(IP_RECORD, 'w') as f:
            f.write(value_new)
        print "RecordList"
        api = apicn.RecordList(DNSPOD['domain_id'], login_token=login_token)
        r = [i for i in api().get("records") if i['name'] == DNSPOD['sub_domain']]
        # print r
        try:
            if value_new != r[0]['value']:
                print "RecordModify"
                logger.info('RecordModify - old value %s, new value %s' % (value_old, value_new))
                api = apicn.RecordModify(r[0]['id'], login_token=login_token, sub_domain=DNSPOD['sub_domain'],
                                         record_type="A", record_line=r[0]['line'], value=value_new, ttl=600,
                                         domain_id=DNSPOD['domain_id'], record_line_id=r[0]['line_id'])
                ret = api()
                if ret['status']['code'] != '1':
                    ## 'record' in ret.keys()
                    print "Record modify failed..."
                print ret
                logger.info(ret)
            else:
                err_msg = "Check dnspod, value(%s) not change, do not need to modify record" % value_new
                print err_msg
                logger.error(err_msg)
        except:
            continue


if __name__ == '__main__':
    main()
