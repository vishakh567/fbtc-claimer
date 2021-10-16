import requests
import time
import sys
import json
import hashlib
import string
from io import StringIO
from bs4 import BeautifulSoup
from random import randint, choice
from datetime import datetime
from urllib.parse import quote
from crontab import CronTab

turl = 'https://api.telegram.org/bot<key>'
debug = 0
chatID = '<chat_id>'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
ACCEPT     = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
COOKIE     = ''
csrf_token = ''
user_id    = '<fbtc_userid>'
headers    = { 'User-Agent': USER_AGENT, 'Cookie': COOKIE, 'accept' : ACCEPT }
proxies    = {}

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

    crons = CronTab(user='<linux username>')
    crons.remove_all(comment='FBTC')
    job = crons.new(command = 'cd /home/FBTC && /usr/bin/python3 FBTC_WOF.py >> FBTC_WOF.out 2>&1', comment='FBTC')
    job.minute.on(nxt_mn)
    job.hour.on(nxt_hr)
    crons.write()

def findtime(delay):
    cur_time  = int(datetime.now().timestamp())
    return (datetime.fromtimestamp(cur_time + delay).strftime('%d %b %H:%M'))

try:
    with requests.Session() as s:
        r = s.get("https://freebitco.in/?op=home", headers = headers, proxies = proxies)
        soup = BeautifulSoup(r.content, 'lxml')

    client_seed = soup.find(id='next_client_seed')['value']
    captcha_status = bool(soup.find(id='play_without_captchas_button'))
    email = soup.find(id="edit_profile_form_email")['value']
    
    wof_comment = ''
    wof_status = bool(soup.find(id='bonus_container_free_wof'))

    if (wof_status == True):
        wof_comment = soup.find(id='bonus_container_free_wof').text.replace(' ends in','').replace('Active bonus ','')

    with requests.Session() as s:
        cab = s.get('https://freebitco.in/?op=get_current_address_and_balance&csrf_token='+csrf_token, headers = headers)
        BTC = cab.text.split(':')[2]
        TxnFee = cab.text.split(':')[3]
  
    rp = int(soup.find('div', attrs={'class':'reward_table_box br_0_0_5_5 user_reward_points font_bold'}).text.replace(',', ""))   
    
    try:
        remroll = int(r.text[r.text.find('title_countdown (')+17:r.text.find(');});</script>')])+3
    except:
        remroll = 0

    try:
        p = str(soup.find(id='bonus_container_free_wof'))
        remwof = int(p[p.rfind('free_wof')+10:p.rfind(')})')])+3
    except:
        remwof = 0

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
        if wof_status == True:
            msg.write('\n\n ⚡️ *'+wof_comment+'*')
            msg.write('\n\n🔹 Next WOF : *'+findtime(remwof)+'*')
        if captcha_status == True:
            msg.write('\n🔹 Captcha Status : '+str(captcha_status))
        if payout == 'Ready':
            msg.write('\n🔹 Payout Status : '+payout)
            msg.write('\n🔹 Txn Fee : *'+TxnFee+' BTC*')
        
        setcronjob(remroll)
        
        Telegram(msg.getvalue())

        raise SyncError

    else:
        print (remroll, 'seconds remaining until next roll')
        time.sleep(remroll)

    if wof_status == False:        
        print (datetime.now().strftime('[%d %b] %H:%M:%S')+' Activating WOF bonus')
        try:
            with requests.Session() as s:
                stats = s.get('https://freebitco.in/cf_stats_public/?f=public_stats_initial&csrf_token={csrf_token}', headers = headers, proxies = proxies)
                base  = int(json.loads(stats.text.replace('\'','\''))['rp_prizes'][39]['points'])
        except:
            base = 600
            
        if rp > 2*base:
            for num in range(1,6):
                if (num*base <= rp):
                    wof_no = num
                    
            try:
                with requests.Session() as s:
                    wof = s.get(f'https://freebitco.in/?op=redeem_rewards&id=free_wof_{wof_no}&points=&csrf_token={csrf_token}', headers = headers, proxies = proxies)
                    if wof.text[0] == 's':
                        wof_comment = 'Activated '+str(wof_no)+' WOF with '+str(num*base)+' RP'
                    else:
                        wof = s.get(f'https://freebitco.in/?op=redeem_rewards&id=free_wof_1&points=&csrf_token={csrf_token}', headers = headers, proxies = proxies)
                        if wof.text[0] == 's':
                            wof_comment = 'Unable to Activate '+str(wof_no)+' WOF Bonus'
                        else:
                            wof_comment = 'Unable to Activate WOF Bonus'
            except:
                wof_comment = 'Unable to Activate WOF Bonus'
                    
    with requests.Session() as s:
        r = s.get("https://freebitco.in/?op=home", headers = headers, proxies = proxies)
        soup = BeautifulSoup(r.content, 'lxml')
        rp = int(soup.find('div', attrs={'class':'reward_table_box br_0_0_5_5 user_reward_points font_bold'}).text.replace(',', ""))
        wof_status = bool(soup.find(id='bonus_container_free_wof'))
        try:
            p = str(soup.find(id='bonus_container_free_wof'))
            remwof = int(p[p.rfind('free_wof')+10:p.rfind(')})')])+3
        except:
            remwof = 0

    with requests.Session() as s:
        data = {'csrf_token': csrf_token, 'op': 'free_play', 'fingerprint': fingerprint(), 'client_seed': client_seed, 'fingerprint2': randint(1000000000,9999999999), 'pwc': '0', 'd5c2233cd15f': '1594322467:ed5b7da67d20be0ff3925e62e818f5557208bf00d1e1c8c6f770e9f9b29df50c', 'f53d8b816e9d': hashlib.sha256(s.get(f'https://freebitco.in/cgi-bin/fp_check.pl?s=f53d8b816e9d&csrf_token={csrf_token}', headers={'x-csrf-token': csrf_token, 'X-Requested-With': 'XMLHttpRequest'}).text.encode('utf-8')).hexdigest()}
        roll = requests.post('https://www.freebitco.in/', data = data, headers = headers, proxies = proxies)

    if roll.text[0] == 's':
        print(datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Free Roll Played')
        remroll = 3605
    else:
        print(datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Free Roll Not Played')
        remroll = 300

    with requests.Session() as s:
        cab = s.get('https://freebitco.in/?op=get_current_address_and_balance&csrf_token='+csrf_token, headers = headers)
        BTC = cab.text.split(':')[2]
        
    msg = StringIO()
    if (wof_comment == 'Unable to Activate WOF Bonus' or remroll == 300):
        msg.write('🛑 ')
    else:
        msg.write('❇️')
        
    msg.write(' FBTC Status from Server')
    msg.write('\n\n'+email)
    msg.write('\n\n🔸 Balance : *'+BTC+' BTC*')
    msg.write('\n🔸 *'+str(rp)+'* Reward Points')
    msg.write('\n🔺 Next Roll : *'+findtime(remroll)+'*')        
    if wof_status == True:
        msg.write('\n\n ⚡️ *'+wof_comment+'*')
        
    setcronjob(remroll)

    with requests.Session() as s:
        wof_page = s.get('https://freebitco.in/cgi-bin/api.pl?op=get_wof_free_spins', headers = headers, proxies = proxies)
        free_spins = int(wof_page.json()['token_count'])
        tokens = wof_page.json()['tokens']

    if free_spins > 0:
        try:
            for token in tokens:
                print (datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Playing Wheel of Fortune')
                client_seed = ''.join(choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
                with requests.Session() as s:
                    r = s.get(f'https://freebitco.in/cgi-bin/wof.pl?u={user_id}&t={token}&cs={client_seed}&captchaType=no-captcha-type&captchaResponse=no-captcha-response', headers = headers, proxies = proxies)
                    res = r.json()                
                    if ('status' in res.keys()):
                        if res['status'] == 'success':
                            msg.write('\n ')
                            if 'prize' in res.keys():
                                if 'rp_' in res['prize'] :
                                    msg.write('♦️ *'+str(res['prize_value'])+' reward points*')
                                elif 'lot_' in res['prize'] :
                                    msg.write('🎟 *'+str(res['prize_value'])+' lottery tickets*')
                                elif 'gt_' in res['prize'] :
                                    msg.write('🎫 *'+str(res['prize_value'])+' golden tickets*')
                                elif 'sat_' in res['prize'] :
                                    msg.write('💵 *'+str(res['prize_value'])+' satoshis*')
                                elif 'gc_' in res['prize'] :
                                    msg.write('🎁 *'+str(res['prize_value'])+' Amazon GV*')
                                elif 'iphone' in res['prize'] :
                                    msg.write('📱 *'+str(res['prize_value'])+' BTC Jackpot Iphone*')
                                elif 'rolex' in res['prize'] :
                                    msg.write('⌚️ *'+str(res['prize_value'])+' BTC Jackpot Rolex*')
                            else:
                                msg.write(str(res))
                        else:
                            msg.write('\n ❌ WOF Roll Failed ')
        except:
            msg.write('\n ❌ WOF Roll Site not accessible ')
            
    if wof_status == True:
        msg.write('\n\n🔹 Next WOF : *'+findtime(remwof)+'*')
    if captcha_status == True:
        msg.write('\n🔹 Captcha Status : '+str(captcha_status))
    if payout == 'Ready':
        msg.write('\n🔹 Payout Status : '+payout)
        msg.write('\n🔹 Txn Fee : *'+TxnFee+' BTC*')
    
    Telegram(msg.getvalue())

except SyncError:
    pass

except:
    pass
    print (datetime.now().strftime('[%d %b] %H:%M:%S')+' --- Didn\'t work')
    Telegram('🛑 '+datetime.now().strftime('[%d %b] %H:%M:%S')+'\n --- Server FBTC didn\'t work ---')
    setcronjob(300)
    sys.exit()

