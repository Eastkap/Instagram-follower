import requests
from selenium import webdriver
import json
import time
import random
from bs4 import BeautifulSoup
import urllib.parse
#import filelock
import pickle
from multiprocessing import Process, Queue, Lock
from discord_hooks import Webhook
from utils import *


#global settings
wh = 'https://discordapp.com/api/webhooks/461546770770558986/ojl-N8wYT3yH8VdmIp0cNk1lPGvZ-h1sAw-L6SlSHyV9gNIh0g71AoL_MwJyHxTPkKxO'



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
lock = Lock()

def get_len(file):
    try:
        with open(file,'r') as f:
            return len(f.read().splitlines())
    except:
        return 0
    #return

#letsgetit
def get_id(username):
    who=username
    rep=requests.get('https://instagram.com/'+who)
    soup=BeautifulSoup(rep.text,'html.parser')
    try:
        qid=str(soup.find_all('script')[3])[str(soup.find_all('script')[3]).index('"id"'):].split('"')[3]
    except:
        qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[2]

    #print(qid)
    return qid

def query_followers(session,many,username):


    url='https://www.instagram.com/graphql/query/?query_id=17851374694183129&variables={"id":"'+get_id(username)+'","first":'+str(many)+'}'
    r=session.get(url,headers=headers)

    #print(url)

    return r.text

def query_followers_v2(session,many,username,logger):

    followers = []
    id_username = get_id(username)

    url = 'https://www.instagram.com/graphql/query/?query_hash=37479f2b8209594dde7facb0d904896a&variables={"id":"'+str(id_username)+'","first":50}'

    reponse = session.get(url,headers=headers)

    data = reponse.json()
    query_info =  data['data']['user']['edge_followed_by']["page_info"]
    for profil in data['data']['user']['edge_followed_by']['edges']:
        pid = profil["node"]["id"]
        p_username = profil["node"]["username"]

        followers.append([pid,p_username])


    while len(followers) < many:
        if not query_info["has_next_page"]:
            logger.warn('no more followers')
            #print('no more followers')
            return followers
        
        

        url = 'https://www.instagram.com/graphql/query/?query_hash=37479f2b8209594dde7facb0d904896a&variables={"id":"'+str(id_username)+'","first":50,"after":"'+str(query_info["end_cursor"])+'"}'
        reponse = session.get(url,headers=headers)

        data = reponse.json()
        query_info =  data['data']['user']['edge_followed_by']["page_info"]
        for profil in data['data']['user']['edge_followed_by']['edges']:
            pid = profil["node"]["id"]
            p_username = profil["node"]["username"]

            followers.append([pid,p_username])
    logger.log('query more followers, len rn is {}'.format(len(followers)))
    return followers

def writefile(path,data):
    try:
        with open(path, 'w') as f:
            f.writelines(data)
        return True
    except:
        return False


def query_following(session,many):

    rep=session.get('https://instagram.com')
    soup=BeautifulSoup(rep.text,'html.parser')
    try:
        qid=str(soup.find_all('script')[3])[str(soup.find_all('script')[3]).index('"id"'):].split('"')[3]
    except:
        qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[2]

    baseurl='https://www.instagram.com/graphql/query/?query_id=17874545323001329&variables='+'{"id":"'+qid+'","first":'+str(many)+'}'


    r=session.get(baseurl)

    data=json.loads(r.text)
    nombre=data["data"]["user"]["edge_follow"]["count"]

    baseurl='https://www.instagram.com/graphql/query/?query_id=17874545323001329&variables='+'{"id":"'+qid+'","first":'+str(nombre)+'}'


    r=session.get(baseurl)


    return r.text

def query_following_v2(session,many,username,logger):

    following = []
    id_username = get_id(username)

    url = 'https://www.instagram.com/graphql/query/?query_hash=58712303d941c6855d4e888c5f0cd22f&variables={"id":"'+str(id_username)+'","first":50}'

    reponse = session.get(url,headers=headers)

    data = reponse.json()
    query_info =  data['data']['user']['edge_follow']["page_info"]
    for profil in data['data']['user']['edge_follow']['edges']:
        pid = profil["node"]["id"]
        p_username = profil["node"]["username"]

        following.append([pid,p_username])

    while len(following) < many:
        if not query_info["has_next_page"]:
            logger.warn('no more followers')
            #print('no more followers')
            return following
        
        

        url = 'https://www.instagram.com/graphql/query/?query_hash=58712303d941c6855d4e888c5f0cd22f&variables={"id":"'+str(id_username)+'","first":50,"after":"'+str(query_info["end_cursor"])+'"}'
        reponse = session.get(url,headers=headers)

        data = reponse.json()
        query_info =  data['data']['user']['edge_follow']["page_info"]
        for profil in data['data']['user']['edge_follow']['edges']:
            pid = profil["node"]["id"]
            p_username = profil["node"]["username"]

            following.append([pid,p_username])
    logger.log('query more followers, len rn is {}'.format(len(following)))
    return following

def getheaders(csrf,iden,mode):
    hdr={
      'authority':'www.instagram.com',
    'method':'POST',
    'path':'/web/friendships/'+str(iden)+'/'+mode+'/',
    'scheme':'https',
    'accept':'*/*',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'en-US,en;q=0.9,fr;q=0.8,es;q=0.7,it;q=0.6',
    'content-length':'0',
    'content-type':'application/x-www-form-urlencoded',
    'dnt':'1',
    'origin':'https://www.instagram.com',
    'referer':'https://www.instagram.com/eastkap/following/',
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'x-csrftoken':csrf,
    'x-instagram-ajax':'1',
    'x-requested-with':'XMLHttpRequest'
    }
    return hdr

def log(data,q):
    print(data)
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36")
    options.add_argument('window-size=600x300')
    #driver = webdriver.Chrome(chrome_options=options)
    try:
        driver = webdriver.Chrome(chrome_options=options)
    except:
        driver = webdriver.Chrome('./chromedriver',chrome_options=options)

    
    url='https://www.instagram.com/accounts/login/'
    driver.get(url)

    time.sleep(1)

    #driver.find_element_by_css_selector("#react-root > section > main > article > div._kbq82 > div:nth-child(2) > p > a").click()
    time.sleep(1)
    try:
        driver.find_element_by_name("username").send_keys(data["username"])
    except Exception as e:
        print(e)
        print(110)


    time.sleep(1)

    driver.find_element_by_name("password").send_keys(data["password"])

    time.sleep(1)

    #driver.find_element_by_css_selector("#react-root > section > main > article > div._kbq82 > div:nth-child(1) > div > form > span > button").click()
    q.get(True)

    gateaux=driver.get_cookies()
    driver.quit()

    return gateaux

def unfollow_old(data,q,logger):
    oldd=data
    combien=data["number"]
    username = data["username"]

    try :
        gateaux = pickle.load( open( data["username"]+"cookies.p", "rb" ) )
    
    except:
        gateaux=log(data,q)
        pickle.dump( gateaux, open( data["username"]+"cookies.p", "wb" ) )

    s=requests.Session()
    s.get('https://www.instagram.com/')
    c = [s.cookies.set(c['name'], c['value']) for c in gateaux]

    a=s.get('https://www.instagram.com/')
    csrf=json.loads(str(a.text).split('window._sharedData = ')[1].split(';')[0])['config']['csrf_token']

    unfurl='https://www.instagram.com/web/friendships/{}/unfollow/?hl=en'

    r=query_following_v2(s,combien,username,logger)

    #data['data']['user']['edge_follow']['edges'].reverse()

    count=0
    for profil in r:
        if count<int(combien):
            count+=1
        else:
            return

        idunf=profil[0]

        headers=getheaders(csrf,idunf,"unfollow")

        #print(headers)
        #print(unfurl.format(str(idunf)))
        a=s.post(unfurl.format(str(idunf)),headers=headers)

        hlp=0
        while(a.status_code!=200):
            hlp+=1
            if hlp>3:
                print("over for the day")
                return
            else:
                print('error: ',a.status_code)
                time.sleep(random.randint(60,180))
                a=s.post(unfurl.format(str(idunf)),headers=headers)

        print(oldd["username"],' has unfollowed ',profil)
        time.sleep(random.randint(40,60))

def unfollow_new(data,q,logger):

    #lock = filelock.FileLock("my_lock_file")


    combien=int(data["number"])

    try :
        gateaux = pickle.load( open( data["username"]+"cookies.p", "rb" ) )
    
    except:
        gateaux=log(data,q)
        pickle.dump( gateaux, open( data["username"]+"cookies.p", "wb" ) )

    s=requests.Session()
    s.get('https://www.instagram.com/')
    c = [s.cookies.set(c['name'], c['value']) for c in gateaux]

    a=s.get('https://www.instagram.com/')
    soup=BeautifulSoup(a.text,'html.parser')
    try:
        qid=str(soup.find_all('script')[3])[str(soup.find_all('script')[3]).index('"id"'):].split('"')[3]
    except:
        qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[2]


    #get id


    csrf=json.loads(str(a.text).split('window._sharedData = ')[1].split(';')[0])['config']['csrf_token']
    unfurl='https://www.instagram.com/web/friendships/{}/unfollow/'


    with lock:
        with open('./'+qid+'following.txt','r') as file:
            users=file.readlines()

    for i in range(combien):

        item = users[0]
        users.remove(item)
        idunf = item[:-1]

        try:
            if not int(idunf)>0:
                
                logger.error("check your unfollow file: "+str(qid)+"following.txt")
        except Exception as e:
            logger.error("check your unfollow file: "+str(qid)+"following.txt"+str(e))


        count=0
        headers=getheaders(csrf,idunf,"unfollow")
        a=s.post(unfurl.format(str(idunf)),headers=headers)


        while(a.status_code!=200 and a.status_code!=400):
            count+=1
            if count>3:
                logger.status("over for the day")
                return
            else:
                logger.warn('error: {}'.format(a.status_code))
                time.sleep(random.randint(60,180))
                a=s.post(unfurl.format(str(idunf)),headers=headers)

        logger.log("{} {} {}".format(data["username"],' has unfollowed ',idunf))

        shutdown = False
        with lock:
            a=False
            sd=False
            while(not a):
                try:
                    a=writefile('./'+qid+'following.txt',users)
                except KeyboardInterrupt:
                    shutdown=True
                    print('shutting down')
        if shutdown:
            return

        time.sleep(random.randint(40,60))

def massfollow(data,q):

    #lock = filelock.FileLock("my_lock_file")


    oldd=data
    combien=data["number"]
    username=data["account2follow"]
    try :
        gateaux = pickle.load( open( data["username"]+"cookies.p", "rb" ) )
    
    except Exception as e:
        gateaux=log(data,q)
        pickle.dump( gateaux, open( data["username"]+"cookies.p", "wb" ) )

    s=requests.Session()
    s.get('https://www.instagram.com/')
    c = [s.cookies.set(c['name'], c['value']) for c in gateaux]

    a=s.get('https://www.instagram.com/')
    soup=BeautifulSoup(a.text,'html.parser')
    try:
        qid=str(soup.find_all('script')[3])[str(soup.find_all('script')[3]).index('"id"'):].split('"')[3]
    except:
        qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[2]

    f=s.get('https://www.instagram.com/'+data["account2follow"]+'/followers/')
    csrf=json.loads(str(a.text).split('window._sharedData = ')[1].split(';')[0])['config']['csrf_token']
    unfurl='https://www.instagram.com/web/friendships/{}/follow/'

    r=query_followers(s,combien,username)

    #print(r)

    data=json.loads(r)

    #print(data)

    for profil in data['data']['user']['edge_followed_by']['edges']:
        idunf=profil['node']['id']

        headers=getheaders(csrf,idunf,"follow")

        #print(headers)

        a=s.post(unfurl.format(str(idunf)),headers=headers)

        with lock:
            with open('./'+qid+'following.txt','a') as file:
                file.write(idunf+'\n')

        count=0
        while(a.status_code!=200):
            count+=1
            print('errorA: ',a.status_code)

            if count>3 and count <5:
                time.sleep(600)
            elif count>=5:
                print("account not following anymore (instagram rules boy)")
                return
            else:
                time.sleep(random.randint(60,180))
            a=s.post(unfurl.format(str(idunf)),headers=headers)

        print(oldd["username"],' has followed ',profil['node']['username'])
        time.sleep(random.randint(20,30))

def get_pics(session,profile,n,logger):
    try:
        response=session.get("http://instagram.com/"+profile)

        aso=response.text.split("window._sharedData =")[1]
        donnees=json.loads(aso.split(";")[0][1:])

        picsids=[]
        try:
            for i in range(n):
                picsids.append(str(donnees["entry_data"]['ProfilePage'][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][i]["node"]["id"]))
        except Exception as ee:

            logger.error('error getting pid id'+str(ee))
            pass

        #print(picsids)
        return picsids
    except Exception as e:
        logger.error(str(e))
        return []

def get_pics_v2(session,profile,n):#ne marche pas
    try:
        #response=session.get("http://instagram.com/"+profile)
        response=session.get("https://www.instagram.com/supcommunity")
        print(str(response.content))
        soup = BeautifulSoup(response.text,'html.parser')
        liens = soup.find_all('a')

        i = 0
        photos = []
        for lien in liens:
            print(lien)
            if '/p/' in lien['href']:
                i+=1
                photos.append('https://www.instagram.com'+lien['href'])
            if i==n:
                break
        print(photos)
        return photos
    except Exception as e:
        print(e)
        return []

def like(session,picid,csrf,logger):
    try:
        hdr={
            'authority':'www.instagram.com',
            'method':'POST',
            'path':'/web/likes/'+picid+'/like/?hl=en',
            'scheme':'https',
            'accept':'*/*',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-US,en;q=0.9,fr;q=0.8,es;q=0.7,it;q=0.6',
            'content-length':'0',
            'content-type':'application/x-www-form-urlencoded',
            'dnt':'1',
            'origin':'https://www.instagram.com',
            'referer':'https://www.instagram.com/eastkap/following/',
            'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'x-csrftoken':csrf,
            'x-instagram-ajax':'1',
            'x-requested-with':'XMLHttpRequest'
        }
        session.post("https://www.instagram.com/web/likes/"+picid+"/like/?hl=en",headers=hdr)

    except Exception as e:
        logger.error(str(e))
        pass

def liketab(session,tab,csrf,logger):
    try:
        for picid in tab:
            like(session,picid,csrf,logger)
    except Exception as e:
        logger.error(str(e))

def massfollow_like(data,q,logger):
    #lock = filelock.FileLock(".lock")
    try:
        oldd=data
        combien=data["number"]
        username=data["account2follow"]

        try :
            gateaux = pickle.load( open( data["username"]+"cookies.p", "rb" ) )
        
        except:
            gateaux=log(data,q)

            pickle.dump( gateaux, open( data["username"]+"cookies.p", "wb" ) )
        

        s=requests.Session()
        s.get('https://www.instagram.com/')
        c = [s.cookies.set(c['name'], c['value']) for c in gateaux]

        a=s.get('https://www.instagram.com/')
        soup=BeautifulSoup(a.text,'html.parser')
        try:
            qid=str(soup.find_all('script')[3])[str(soup.find_all('script')[3]).index('"id"'):].split('"')[3]
        except:
            qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[2]

        f=s.get('https://www.instagram.com/'+data["account2follow"]+'/followers/')
        csrf=json.loads(str(a.text).split('window._sharedData = ')[1].split(';')[0])['config']['csrf_token']
        unfurl='https://www.instagram.com/web/friendships/{}/follow/'

        follower_ids=query_followers_v2(s,combien,username,logger)


        for combo in follower_ids:
            logger.log(combo)

            idunf=combo[0]
            p_username = combo[1]

            headers=getheaders(csrf,idunf,"follow")

            #print(headers)

            a=s.post(unfurl.format(str(idunf)),headers=headers)

            with lock:
                with open('./'+qid+'following.txt','a') as file:
                    file.write(idunf+'\n')

            count=0

            #print(oldd["pics2like"])
            pics2like = get_pics(s,p_username,oldd["pics2like"],logger)
            logger.log(pics2like)
            liketab(s,pics2like,csrf,logger)

            while(a.status_code!=200):
                count+=1
                logger.warn('errorA: ',a.status_code)

                if count>3 and count <5:
                    time.sleep(600)
                elif count>=5:
                    logger.error("account not following anymore (instagram rules boy)")
                    return
                else:
                    time.sleep(random.randint(60,180))
                a=s.post(unfurl.format(str(idunf)),headers=headers)

            


            #print(oldd["username"],' has followed ',p_username)
            logger.log("{} has followed {}".format(oldd["username"],p_username))
            time.sleep(random.randint(20,30))
    except Exception as e :
        logger.error(str(e))

def load():
    try:
        with open("./config.txt",'r') as file:
            d=file.read()
        data=json.loads(d)
        return data
    except:
        anumber=int(input("how many accounts to set up: "))
        tab=[]
        for i in range(anumber):
            data=dict()
            data["username"]=input("username for account #"+str(i)+": ")
            data["password"]=input("password: ")
            data["account2follow"]=input("which account to follow: ")
            data["number"]=int(input("how many follows to do?"))
            data["mode"]=input("What do you want to do? [F]ollow, [Fo]llow and like, [U]nfollow or [Un]follow with old mode, [B]ackup current followers: ")
            data["pics2like"]=int(input("How many pics do you want to like each time you follow someone: "))
            tab.append(data)


        with open("./config.txt",'w') as file:
            json.dump(tab,file)
        return tab

def backup(data,q):
    try :
        gateaux = pickle.load( open( data["username"]+"cookies.p", "rb" ) )
    
    except:
        gateaux=log(data,q)
        pickle.dump( gateaux, open( data["username"]+"cookies.p", "wb" ) )

    s=requests.Session()

    s.get('https://www.instagram.com/')
    time.sleep(1)
    c = [s.cookies.set(c['name'], c['value']) for c in gateaux]

    a=s.get('https://www.instagram.com/')
    soup=BeautifulSoup(a.text,'html.parser')

    #number=int(str(soup.find_all('script')[2]).split("follows")[1].split(":")[2][1:].split("}")[0])
    number = 10000

    #qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[3]
    #qid=str(soup.find_all('script')[2])[str(soup.find_all('script')[2]).index('"id"'):].split('"')[3]

    qid=json.loads(str(a.text).split('window._sharedData = ')[1].split(';')[0])['config']['viewer']['id']
    #changement pour le nouveau graphql



    print('qid',qid)


    baseurl='https://www.instagram.com/graphql/query/?query_hash=58712303d941c6855d4e888c5f0cd22f&variables='+'{"id":"'+qid+'","first":'+str(number+1200)+'}'

    r=s.get(baseurl)

    print(str(r.content))

    d=json.loads(r.text)


    with open("./backup"+data["username"]+".txt",'w') as file:
        for user in  d['data']['user']['edge_follow']['edges']:
            file.write(user['node']['id']+'\n')

    print("backup completed for account: "+data["username"])

def follow_backup(data,q,lock):
    oldd=data

    try :
        gateaux = pickle.load( open( data["username"]+"cookies.p", "rb" ) )
    
    except:
        gateaux=log(data,q)
        pickle.dump( gateaux, open( data["username"]+"cookies.p", "wb" ) )

    s=requests.Session()
    s.get('https://www.instagram.com/')
    c = [s.cookies.set(c['name'], c['value']) for c in gateaux]

    try:
        a=s.get('https://www.instagram.com/')
    except:
        a = s.get('https://www.instagram.com/',allow_redirects=False)
    soup=BeautifulSoup(a.text,'html.parser')
    qid=str(soup.find_all('script')[3])[str(soup.find_all('script')[3]).index('"id"'):].split('"')[3]

    #get id

    csrf=json.loads(str(a.text).split('window._sharedData = ')[1].split(';')[0])['config']['csrf_token']

    #csrf=a.text[a.text.index('csrf')+14:a.text.index('csrf')+46]
    unfurl='https://www.instagram.com/web/friendships/{}/follow/'

    with open('./backup'+data["username"]+".txt",'r') as file :
        d=file.readlines()

    for i in d:
        idunf = i[:-1]

        headers=getheaders(csrf,idunf,"follow")

        #print(headers)

        a=s.post(unfurl.format(str(idunf)),headers=headers)

        hlp=0
        while(a.status_code!=200 and a.status_code != 400):
            hlp+=1
            if hlp>3:
                print("over for the day")
                return
            else:
                print('error: ',a.status_code)
                time.sleep(random.randint(60,180))
                a=s.post(unfurl.format(str(idunf)),headers=headers)

        print(oldd["username"],' has followed ',idunf)
        time.sleep(random.randint(10,40))

def main():

    q=Queue()

    adata=load()

    threads=[]

    #best launcher in da world i no

    for data in adata:
        if data["mode"]=='F':
            threads.append(Process(target=massfollow,args=(data,q,)))
        elif data["mode"]=='U':
            threads.append(Process(target=unfollow_new,args=(data,q,)))
        elif data["mode"]=='Un':
            threads.append(Process(target=unfollow_old,args=(data,q,)))
        elif data["mode"]=='B':
            threads.append(Process(target=backup,args=(data,q,)))
        elif data["mode"]=='Fo':
            threads.append(Process(target=massfollow_like,args=(data,q,)))
        elif data["mode"]=="FB":
            threads.append(Process(target=follow_backup,args=(data,q,)))


    for p in threads:
        p.daemon=True
        p.start()
        dummy=input("press enter if log-in has gone correctly")
        time.sleep(1)
        q.put(1)

    for p in threads:
        p.join()
        print("one thread ended")

def new_main():
    q=Queue()

    adata=load()
    while True:

        logger = Logger(wh,get_full_date_logging()+'.txt')
        try:
            ini = time.time()

            threads=[]

            #best launcher in da world i no

            for data in adata:
                qid = get_id(data["username"])
                if get_len('{}following.txt'.format(qid)) > 2000:
                    threads.append(Process(target=massfollow_like,args=(data,q,logger,)))
                else:
                    threads.append(Process(target=unfollow_new,args=(data,q,logger,)))
                
            for p in threads:
                p.daemon=True
                p.start()
                time.sleep(1)
                q.put(1)
            
            for p in threads:
                p.join()

            if(time.time()-ini < 60*60*8):
                time.sleep(60)
        except Exception as e:
            logger.error(str(e))


if __name__ == '__main__':
    main()