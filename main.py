import requests, json, os, datetime


def getSongList(uid, page):
    headers = {
        'referer': f'https://static-play.kg.qq.com/node/personal_v2/?uid={uid}&stay=1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }

    params = {
        'outCharset': 'utf-8',
        'from': '1',
        'format': 'json',
        'type': 'get_uinfo',
        'start': page,
        'num': '10',
        'share_uid': uid,
    }

    response = requests.get('https://node.kg.qq.com/fcgi-bin/kg_ugc_get_homepage', params=params, headers=headers)

    return response.json()
    
def getSongInfo(shareid):
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    rsp = requests.get(f"https://kg.qq.com/node/play?s={shareid}")
    
    TEXT_BEFORE_JSON = "window.__DATA__ = "
    TEXT_AFTER_JSON = "; </script>"
    
    content = rsp.text
    start_idx = content.find(TEXT_BEFORE_JSON)
    content = content[start_idx+len(TEXT_BEFORE_JSON):]

    end_idx = content.find(TEXT_AFTER_JSON)
    content = content[:end_idx]

    songInfo = json.loads(content)
    
    return songInfo
    
def downloadSong(url, filepath):
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    }
    
    content = requests.get(url, headers=headers)
    with open(filepath, "wb") as f:
        f.write(content.content)
    
    
share_uid = "share_uid" # https://static-play.kg.qq.com/node/personal_v2/?uid={share_uid}&stay=1

if not os.path.exists(f"./{share_uid}"):
    os.mkdir(f"./{share_uid}")

ugc_list = True
page = 1
while ugc_list:
    ugc_list = getSongList(share_uid, page)['data']['ugclist']
    for i in ugc_list:
        
        song_strid = f"{datetime.datetime.fromtimestamp(i['time']).strftime('%Y%m%d_%H%M%S')}_{i['title']}"
        print(song_strid)
        
        if os.path.exists(f"./{share_uid}/{song_strid}"):
            continue
        
        os.mkdir(f"./{share_uid}/{song_strid}")
        
        with open(f"./{share_uid}/{song_strid}/ugcInfo.json", "w+") as f:
            f.write(json.dumps(i, ensure_ascii=False, separators=(",", ":")))
            
        songInfo = getSongInfo(i['shareid'])
        with open(f"./{share_uid}/{song_strid}/songInfo.json", "w+") as f:
            f.write(json.dumps(songInfo, ensure_ascii=False, separators=(",", ":")))
        
        ts = datetime.datetime.fromtimestamp(songInfo['detail']['ctime']).strftime("%Y%m%d_%H%M%S")
        if songInfo['detail']['playurl']:
            downloadSong(songInfo['detail']['playurl'], f"./{share_uid}/{song_strid}/{ts}_{songInfo['detail']['song_name']}.m4a")
        elif songInfo['detail']['playurl_video']:
            downloadSong(songInfo['detail']['playurl_video'], f"./{share_uid}/{song_strid}/{ts}_{songInfo['detail']['song_name']}.mp4")
        else:
            print("error")
            
    page += 1
