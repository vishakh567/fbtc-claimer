import requests
import time
import sys
import hashlib
from io import StringIO
from bs4 import BeautifulSoup
from random import randint
from datetime import datetime
from urllib.parse import quote
from crontab import CronTab

turl = 'https://api.telegram.org/bot'
debug = 0
chatID = ''

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
ACCEPT     = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
COOKIE     = ''
csrf_token = ''

class SyncError(Exception):
    pass

def Telegram(msg, keyboard=''):
    try:
        res = requests.get(turl+'/sendMessage?chat_id='+chatID+'&parse_mode=Markdown&text='+quote(msg)+'&reply_markup='+quote(keyboard.replace('\'','"')))
        if (debug == 1):
            print (res.text) 
    except:
        print ('Telegram Message not sent')

def fingerprint():
    md5 = hashlib.md5()
    md5.update(('###'.join([USER_AGENT,
                            'x'.join(['1024', '1280', '24']),'-420','true','true',
                            '::'.join(['BookReader', '', 
                                       'application/epub+zip~epub,application/x-fictionbook+xml~fb2,application/x-zip-compressed-fb2~fb2.zip;Chromium PDF Plugin',
                                       'Portable Document Format', 'application/x-google-chrome-pdf~;Chromium PDF Viewer', '', 'application/pdf~pdf;Native Client','',
                                       'application/x-nacl~,application/x-pnacl~;Shockwave Flash',
                                       'Shockwave Flash 32.0 r0::application/x-shockwave-flash~swf,application/futuresplash~spl'
                                        ])])).encode('utf-8'))

    
def setcronjob(delay):
    cur_time   = int(datetime.now().timestamp())
    nxt_time   = cur_time + delay

    nxt_hr = int(datetime.fromtimestamp(nxt_time).strftime('%H'))
    nxt_mn = int(datetime.fromtimestamp(nxt_time).strftime('%M'))

    crons = CronTab(user='vishakh567')
    crons.remove_all(comment='FBTC')
    job = crons.new(command = 'cd /home/vishakh567/FBTC && /usr/bin/python3 FBTC.py >> FBTC.out 2>&1', comment='FBTC')
    job.minute.on(nxt_mn)
    job.hour.on(nxt_hr)
    crons.write()

def findtime(delay):
    cur_time  = int(datetime.now().timestamp())
    return (datetime.fromtimestamp(cur_time + delay).strftime('%d %b %H:%M'))

headers = { 'User-Agent': USER_AGENT, 'Cookie': COOKIE, 'accept' : ACCEPT }
proxies = {}

try:
    with requests.Session() as s:
        r = s.get("https://freebitco.in/?op=home", headers = headers, proxies = proxies)
        soup = BeautifulSoup(r.content, 'lxml')

    client_seed = soup.find(id='next_client_seed')['value']
    captcha_status = bool(soup.find(id='play_without_captchas_button'))
    email = soup.find(id="edit_profile_form_email")['value']
    rpb_comment = ''
    fbb_comment = ''

    rpb_status = bool(soup.find(id='bonus_container_free_points'))
    if (rpb_status == True):
        rpb_comment = soup.find(id='bonus_container_free_points').text.replace(' ends in','').replace('Active bonus ','')
      
    fbb_status = bool(soup.find(id='bonus_container_fp_bonus'))
    if (fbb_status == True):
        fbb_comment = soup.find(id='bonus_container_fp_bonus').text.replace(' ends in','').replace('Active bonus ','')

    with requests.Session() as s:
        cab = s.get('https://freebitco.in/?op=get_current_address_and_balance&csrf_token='+csrf_token, headers = headers)
        BTC = cab.text.split(':')[2]
        
    rp = int(soup.find('div', attrs={'class':'reward_table_box br_0_0_5_5 user_reward_points font_bold'}).text.replace(',', ""))

    try:
        remroll = int(r.text[r.text.find('title_countdown (')+17:r.text.find(');});</script>')])+3
    except:
        remroll = 0

    try:
        p = str(soup.find(id='bonus_container_free_points'))
        remrp = int(p[p.rfind('free_points')+13:p.rfind(')})')])+3
    except:
        remrp = 0

    if float(BTC) > float(0.0010000):
        payout = 'Ready'
    else:
        payout = 'Not Ready'

    if (remroll > 59):
        
        msg = StringIO()
        msg.write('❇️')
        msg.write(' FBTC Status from Server')
        msg.write('\n\n'+email)
        msg.write('\n\n🔸 Balance : *'+BTC+' BTC*')
        msg.write('\n🔸 *'+str(rp)+'* Reward Points')
        msg.write('\n🔺 Next Roll : *'+findtime(remroll)+'*')  
        if rpb_status == True:
            msg.write('\n\n ⚡️ *'+rpb_comment+'*')
        if (fbb_status == True):
            msg.write('\n ⚡️ *'+fbb_comment+'*')
        if rpb_status == True:
            msg.write('\n\n🔹 Next RP : *'+findtime(remrp)+'*')
        if captcha_status == True:
            msg.write('\n🔹 Captcha Status : '+str(captcha_status))
        if payout == 'Ready':
            msg.write('\n🔹 Payout Status : '+payout)
        
        setcronjob(remroll)
        
        Telegram(msg.getvalue())

        raise SyncError

    else:
        print (remroll, 'seconds remaining until next roll')
        time.sleep(remroll)

    if rpb_status == False:
        print (datetime.now().strftime('[%d %b] %H:%M:%S')+' Activating reward point bonus')
        if rp > 11:
            rpbno = 10
            rpbnos = [1,10,25,50,100]
            for num in rpbnos:
                if ((num*12)+12 <= rp):
                    rpbno = num
                    
            try:
                with requests.Session() as s:
                    rpb = s.get(f'https://freebitco.in/?op=redeem_rewards&id=free_points_{rpbno}&points=&csrf_token={csrf_token}', headers = headers, proxies = proxies)
                    if rpb.text[0] == 's':
                        rpb_comment = 'Activated '+str(rpbno)+' RP Bonus'
                    else:
                        rpb = s.get(f'https://freebitco.in/?op=redeem_rewards&id=free_points_10&points=&csrf_token={csrf_token}', headers = headers, proxies = proxies)
                        if rpb.text[0] == 's':
                            rpb_comment = 'Unable to Activate '+str(rpbno)+' RP Bonus'
                        else:
                            rpb_comment = 'Unable to Activate RP Bonus'
            except:
                rpb_comment = 'Unable to Activate RP Bonus'
                    
    with requests.Session() as s:
        r = s.get("https://freebitco.in/?op=home", headers = headers, proxies = proxies)
        rp = int(soup.find('div', attrs={'class':'reward_table_box br_0_0_5_5 user_reward_points font_bold'}).text.replace(',', ""))
        soup = BeautifulSoup(r.content, 'lxml')
        rpb_status = bool(soup.find(id='bonus_container_free_points'))
        fbb_status = bool(soup.find(id='bonus_container_fp_bonus'))
        try:
            p = str(soup.find(id='bonus_container_free_points'))
            remrp = int(p[p.rfind('free_points')+13:p.rfind(')})')])+3
        except:
            remrp = 0

    with requests.Session() as s:
        data = {'csrf_token': csrf_token, 'op': 'free_play', 'fingerprint': fingerprint(), 'client_seed': client_seed, 'fingerprint2': randint(1000000000,9999999999), 'pwc': '0', 'd5c2233cd15f': '1594322467:ed5b7da67d20be0ff3925e62e818f5557208bf00d1e1c8c6f770e9f9b29df50c', 'f53d8b816e9d': hashlib.sha256(s.get(f'https://freebitco.in/cgi-bin/fp_check.pl?s=f53d8b816e9d&csrf_token={csrf_token}', headers={'x-csrf-token': csrf_token, 'X-Requested-With': 'XMLHttpRequest'}).text.encode('utf-8')).hexdigest()}
        roll = requests.post('https://www.freebitco.in/', data = data, headers = headers, proxies = proxies)

    if roll.text[0] == 's':
        print(datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Free Roll Played')
        remroll = 3610
    else:
        print(datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Free Roll Not Played')
        remroll = 300

    with requests.Session() as s:
        cab = s.get('https://freebitco.in/?op=get_current_address_and_balance&csrf_token='+csrf_token, headers = headers)
        BTC = cab.text.split(':')[2]
        
    msg = StringIO()
    if (rpb_comment == 'Unable to Activate RP Bonus' or remroll == 300):
        msg.write('🛑 ')
    else:
        msg.write('❇️')
        
    msg.write(' FBTC Status from Server')
    msg.write('\n\n'+email)
    msg.write('\n\n🔸 Balance : *'+BTC+' BTC*')
    msg.write('\n🔸 *'+str(rp)+'* Reward Points')
    msg.write('\n🔺 Next Roll : *'+findtime(remroll)+'*')        
    if rpb_status == True:
        msg.write('\n\n ⚡️ *'+rpb_comment+'*')
    if (fbb_status == True):
        msg.write('\n ⚡️ *'+fbb_comment+'*')
    if rpb_status == True:
        msg.write('\n\n🔹 Next RP : *'+findtime(remrp)+'*')
    if captcha_status == True:
        msg.write('\n🔹 Captcha Status : '+str(captcha_status))
    if payout == 'Ready':
        msg.write('\n🔹 Payout Status : '+payout)

    setcronjob(remroll)
        
    Telegram(msg.getvalue())
    
except SyncError:
    pass

except:
    pass
    print (datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Didn\'t work')
    Telegram('🛑 '+datetime.now().strftime('[%d %b] %H:%M:%S')+'\n --- Server FBTC didn\'t work ---')
    setcronjob(300)
    sys.exit()
