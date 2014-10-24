#!/usr/bin/env python
# coding: utf-8
"""
Twitter関連のユーティリティモジュール
"""
import re
import time
import calendar
import HTMLParser

# html special charsをアンエスケープするためのパーサ
parser = HTMLParser.HTMLParser()

def get_text_and_entities(tw):
    """
    ツイートを渡すと，エンティティ除外文書とエンティティリストを返す
    """
    if 'entities' in tw:
        return _get_text_and_entities_ent(tw)
    else:
        return _get_text_and_entities_reg(tw)

def _get_text_and_entities_ent(tw):
    """
    entities情報を用いて，エンティティ除外文書とエンティティリストを返す
    URLが存在するにも関わらず，entities情報にはないということがあったので
    正規表現もあわせて用いて抽出を行う
    """
    raw_text = tw['text']
    entities = tw['entities']
    indices  = []
    urls     = []
    mentions = []
    hashtags = []
    # entitiesを取得
    if 'urls' in entities:
        for url in entities['urls']:
            urls.append(url['url'])
            indices.append(url['indices'])
    if 'user_mentions' in entities:
        for mention in entities['user_mentions']:
            mentions.append(mention['screen_name'])
            indices.append(mention['indices'])
    if 'hashtags' in entities:
        for hashtag in entities['hashtags']:
            hashtags.append(hashtag['text'])
            indices.append(hashtag['indices'])
    # textからentitiesを除外
    cur = 0
    text = ''
    for i, indice in enumerate(sorted(indices, key=lambda x:x[0])):
        text += raw_text[cur:indice[0]]
        cur = indice[1]
    text += raw_text[cur:]
    # 正規表現を用いてentitiesを抽出
    text, ent_reg = _get_text_and_entities_reg({'text': text})
    if 'urls' in ent_reg:
        urls += ent_reg['urls']
    if 'mentions' in ent_reg:
        mentions += ent_reg['mentions']
    if 'hashtags' in ent_reg:
        hashtags += ent_reg['hashtags']
    # entitiesの保存
    entities = {}
    if urls:
        entities['urls'] = urls
    if mentions:
        entities['mentions'] = mentions
    if hashtags:
        entities['hashtags'] = hashtags
    return text, entities

def _get_text_and_entities_reg(tw):
    """
    正規表現を用いて，エンティティ除外文書とエンティティリストを返す
    """
    text = tw['text'] if tw['text'] else ''
    urls = get_urls(text)
    mentions = get_mentions(text)
    hashtags = get_hashtags(text)
    entities = urls + mentions + hashtags
    for entity in entities:
        text = text.replace(entity, '')
    entities = {}
    if urls:
        entities['urls'] = urls
    if mentions:
        entities['mentions'] = mentions
    if hashtags:
        entities['hashtags'] = hashtags
    return unescape(text), entities

def get_urls(s):
    """
    文字列からURLを抽出して返す
    URLに使用可能な文字は以下を参照
        http://tools.ietf.org/html/rfc2396
        http://jbpe.tripod.com/rfcj/rfc2396.ej.sjis.txt（日本語訳）
    正規表現の特殊文字は以下を参照
        http://www.python.jp/doc/release/library/re.html#module-re
    """
    r = re.compile(r"https?://[\w;/?:@&=+$,\-.!~*'()%]+")
    return r.findall(s)

def get_mentions(s):
    """
    文字列から@screen_nameを抽出して返す
    @screen_nameに使用可能な文字は英数字とアンダースコアで15文字以下
    adminやtwitterが含まれるものは不可
    以下を参照
        https://support.twitter.com/groups/31-twitter-basics/topics/104-welcome-to-twitter-support/articles/230266-#
    """
    r = re.compile(r'@\w+')
    return r.findall(s)

def get_hashtags(s):
    """
    文字列から#hashtagを抽出して返す
    ハッシュタグに句読 ( , . ; ' ? ! 等) が含まれると、その句読までの文字がハッシュタグとして扱われる
    以下を参照
    ハッシュ記号#の直前はスペースである必要がある
        https://support.twitter.com/articles/450254-#
        http://d.hatena.ne.jp/sutara_lumpur/20101012/1286860552
    """
    r = re.compile(
            u'(^|[^ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９\w&/]+)(' +
            u'[#＃]' +
            u'[ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９\w]*' +
            u'[ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９a-zA-Z]+' +
            u'[ｦ-ﾟー゛゜々ヾヽぁ-ヶ一-龠ａ-ｚＡ-Ｚ０-９\w]*)'
            )
    return [x[1] for x in r.findall(s)]

def twittertime2unixtime(twitter_time):
    """
    Twitter時間からUNIX時間に変換
    """
    unix_time = calendar.timegm(time.strptime(twitter_time, '%a %b %d %H:%M:%S +0000 %Y'))
    return unix_time

def twittertime2localtime(twitter_time):
    """
    Twitter時間からローカル時間（日本時間）に変換
    """
    unix_time = calendar.timegm(time.strptime(twitter_time, '%a %b %d %H:%M:%S +0000 %Y'))
    return time.localtime(unix_time)

def unixtime2localtime(unix_time):
    """
    UNIX時間からローカル時間（日本時間）に変換
    """
    return time.localtime(unix_time)

def unixtime2twittertime(unix_time):
    """
    UNIX時間からTwitter時間に変換
    """
    return time.strftime('%a %b %d %H:%M:%S +0000 %Y', time.gmtime(unix_time))

def localtime2unixtime(local_time):
    """
    ローカル時間（日本時間）からUNIX時間に変換
    """
    return time.mktime(local_time)

def localtime2twittertime(local_time):
    """
    ローカル時間（日本時間）からTwitter時間に変換
    """
    unix_time = time.mktime(local_time)
    return time.strftime('%a %b %d %H:%M:%S +0000 %Y', time.gmtime(unix_time))

def unescape(text):
    """
    html special charsをアンエスケープして元の文字列に戻す
    """
    return parser.unescape(text)

def unescape_dquote(text):
    """
    MeCab辞書の文字列がダブルクォーテーションで囲まれていた場合
    通常の文字列に直して返す
    """
    if text[0] == '"' and text[-1] == '"':
        text = text[1:-1].replace('""', '"')
    return text

