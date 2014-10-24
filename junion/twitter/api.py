#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import urllib2
import oauth2
import time
import numpy as np

class API(object):
    def __init__(self,
            consumer_key=None,
            consumer_secret=None,
            access_token=None,
            access_token_secret=None,
            oauth_file=None,
            api_host='https://api.twitter.com',
            stream_host='https://stream.twitter.com',
            version='1.1',
            proxy=None,
            retry_count=0,
            retry_delay=0,
            ):

        self.api_host = api_host
        self.stream_host = stream_host
        self.version = version
        self.proxy = proxy
        self.retry_count = retry_count
        self.retry_delay = retry_delay

        if proxy:
            os.environ['HTTP_PROXY']  = proxy
            os.environ['HTTPS_PROXY'] = proxy

        if oauth_file:
            self._load_oauth_file(oauth_file)
        else:
            consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
            token = oauth2.Token(key=access_token, secret=access_token_secret)
            self.oauths = [{'consumer': consumer, 'token': token}]
        self.oauth_index = 0

    def _load_oauth_file(self, oauth_file):
        self.oauths = []
        with open(oauth_file) as file:
            for line in file:
                js = json.loads(line)
                consumer = oauth2.Consumer(key=js['consumer_key'], secret=js['consumer_secret'])
                token = oauth2.Token(key=js['access_token'], secret=js['access_token_secret'])
                self.oauths.append({'consumer': consumer, 'token': token})

    def _request(self, category, name, params, extension='json'):
        url = os.path.join(self.api_host, self.version, category, '%s.%s' % (name, extension))
        for i in xrange(self.retry_count + 1):
            try:
                consumer = self.oauths[self.oauth_index]['consumer']
                token = self.oauths[self.oauth_index]['token']
                req = oauth2.Request.from_consumer_and_token(consumer, token, http_url=url, parameters=params)
                req.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
                res = urllib2.urlopen(req.to_url())
                return json.load(res)
            except urllib2.URLError, e:
                # Unauthorized: protected
                if e.code == 401:
                    raise e
                # Not Found: deleted
                elif e.code == 404:
                    raise e
                # Too Many Requests: rate limit exceeded
                elif e.code == 429:
                    sys.stderr.write('oauths[%d] reaches the rate limit.' % self.oauth_index)
                    self._change_oauth(category, name)
                # otherwise
                else:
                    pass

    def _change_oauth(self, category, name):
        length = len(self.oauths)
        resets = [0] * length
        for i in xrange(length):
            self.oauth_index = (self.oauth_index + 1) % length
            rls = self.rate_limit_status(resources=category)
            remaining = rls['resources'][category][name]['remaining']
            # remainingがあれば現在のOAuthを採用
            if remaining:
                return
            reset = rls['resources'][category][name]['reset']
            resets[self.oauth_index] = reset
        # すべてのremainingが0なら最短時間wait
        self.oauth_index = np.argmin(resets)
        time.sleep(int(resets[self.oauth_index] - time.time() + 1))

    def rate_limit_status(self, resources=None):
        params = {}
        if resources:
            params['resources'] = resources
        return self._request('application', 'rate_limit_status', params)

    def user_timeline(self,
            user_id=None,
            screen_name=None,
            since_id=None,
            count=None,
            max_id=None,
            trim_user=None,
            exclude_replies=None,
            contributor_details=None,
            include_rts=None,
            ):
        params = {}
        if user_id:
            params['user_id'] = user_id
        if screen_name:
            params['screen_name'] = screen_name
        if since_id:
            params['since_id'] = since_id
        if count:
            params['count'] = count
        if max_id:
            params['max_id'] = max_id
        if trim_user:
            params['trim_user'] = trim_user
        if exclude_replies:
            params['exclude_replies'] = exclude_replies
        if contributor_details:
            params['contributor_details'] = contributor_details
        if include_rts:
            params['include_rts'] = include_rts
        return self._request('statuses', 'user_timeline', params)

