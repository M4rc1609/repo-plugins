'''
    FilmOn plugin for XBMC
    Copyright (C) 2012 FilmOn.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
from datetime import date
from datetime import datetime
import settings
from hashlib import md5
import json
from threading import Timer
from t0mm0.common.net import Net
net = Net()
ADDON = xbmcaddon.Addon(id='plugin.video.filmon')
resolution=ADDON.getSetting('res')
language = ADDON.getLocalizedString

#Global Constants
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
channel= 'http://www.filmon.com/channel/'
logo = 'http://static.filmon.com/couch/channels/'
api ='http://www.filmon.com/api/'
tvapi='http://www.filmon.com/tv/api/'
user=ADDON.getSetting('user')
passs=ADDON.getSetting('pass')
password = md5(passs).hexdigest()
keep_alive='http://www.filmon.com/api/keep-alive?session_key='
filmon='http://www.filmon.com/tv/themes/filmontv/img/mobile/filmon-logo-stb.png'
def keepAlive():
    validWin = xbmcgui.getCurrentWindowId() in [10025, 12005]
    if not validWin:
        print '=======================Ending Session======================='
        sess = xbmcgui.Window(10000).getProperty("SessionID")
        logout=api+'logout?session_key=%s' % (sess)
        req =urllib2.Request(logout)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        print '===============LOGGED OUT !!==============='
        xbmcgui.Window(10000).clearProperty("SessionID")
        return

    print '=======================KEEPING THE SESSION ALIVE !!==========================='
    ses = xbmcgui.Window(10000).getProperty("SessionID")
    urllib2.urlopen(keep_alive+ses)
    t = Timer(30.0, keepAlive)
    t.start()

if not xbmcgui.Window(10000).getProperty("SessionID"):
    #Starting Session
    url= api+'init/'
    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(req)
    link=response.read()
    match= re.compile('"session_key":"(.+?)"').findall (link)
    sess=match[0]
    if ADDON.getSetting('filmon') == 'true':
            log=api+'login?session_key=%s&login=%s&password=%s' % (sess,user,password)
            req =urllib2.Request(log)
            req.add_header('User-Agent', USER_AGENT)
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()    
            xbmcgui.Window(10000).setProperty("SessionID", sess)
            keepAlive()
            print '=======================LOGGED IN !! ==========================='
    if ADDON.getSetting('filmon') == 'false':
            xbmcgui.Window(10000).setProperty("SessionID", sess)
            keepAlive()
            print '=======================NOT LOGGED IN !! ==========================='
            
if ADDON.getSetting('filmon') == 'true':
        ADDON.setSetting(id='firstrun', value='true')
ses = xbmcgui.Window(10000).getProperty("SessionID")


                
def CATEGORIES():       
        if ADDON.getSetting('filmon') == 'true':
                addDir(language(30059),'url',5,'http://www.filmon.com/tv/themes/filmontv/img/mobile/filmon-logo-stb.png','','','','','','','','')
        if ADDON.getSetting('filmon') == 'true':
                        addDir(language(30060),'url',9,'http://www.filmon.com/tv/themes/filmontv/images/category/favorites_stb.png','','','','','','','','')                                
        grp='http://www.filmon.com/api/groups?session_key=%s' % (ses)
        link = net.http_GET(grp).content
        data = json.loads(link)
        for field in data:
                url = field['group_id']
                name = field['group']
                iconimage= field['logo_148x148_uri']
                addDir(name,url,3,iconimage,'','','','','','','','')
                setView('tvshows', 'default') 
        
def Channels(name,url):
        if ADDON.getSetting('firstrun') == 'false':
                dialog = xbmcgui.Dialog()
                if dialog.yesno(language(30021),language(30022),'',language(30023),language(30024),language(30025)):
                        if dialog.yesno(language(30021),'','   ',language(30026),language(30027),language(30028)):
                                keyemail = None
                                keyboard = xbmc.Keyboard('', language(30307))
                                keyboard.doModal()
                                if keyboard.isConfirmed():
                                    keyemail = keyboard.getText()
                                if keyemail == None:
                                    return False
                                    
                                keypassword = None
                                keyboard = xbmc.Keyboard('', language(30308))
                                keyboard.doModal()
                                if keyboard.isConfirmed():
                                    keypassword = keyboard.getText()
                                if keypassword == None:
                                    return False   
                                try:
                                        res='http://www.filmon.com/api/register?session_key=%s&email=%s&password=%s' % (ses,keyemail,keypassword)
                                        req = urllib2.Request(res)
                                        req.add_header('User-Agent', USER_AGENT)
                                        response = urllib2.urlopen(req)
                                        link=response.read() 
                                        if re.search((keyemail),link):
                                            ADDON.setSetting('user', value=keyemail)
                                            ADDON.setSetting('pass', value=keypassword)
                                            ADDON.setSetting(id='firstrun', value='true')
                                            ADDON.setSetting(id='filmon', value='true')
                                except:
                                        dialog.ok(language(30021), language(30029), language(30030),language(30031))    
                                try:
                                    country=settings.country()
                                    city = ''
                                    keyboard = xbmc.Keyboard('', language(30309))
                                    keyboard.doModal()
                                    if keyboard.isConfirmed():
                                        city = keyboard.getText()
                                        if city == None:
                                            return False
                                    values ={"country":country,"city":city}
                                    res='http://www.filmon.com/api/accountLocation?session_key=%s' % (ses)
                                    data = urllib.urlencode(values)
                                    req = urllib2.Request(res,data)
                                    req.add_header('User-Agent', USER_AGENT)
                                    response = urllib2.urlopen(req)
                                    link=response.read()
                                    if re.search('Accepted',link):                                                   
                                        dialog.ok(language(30021),language(30032), "",language(30033))
                                except:
                                        dialog.ok(language(30021),language(30034),language(30035),language(30036))
                        else:
                                keyemail = None
                                keyboard = xbmc.Keyboard('', language(30307))
                                keyboard.doModal()
                                if keyboard.isConfirmed():
                                    keyemail = keyboard.getText()
                                if keyemail == None:
                                    return False
                                    
                                keypassword = None
                                keyboard = xbmc.Keyboard('', language(30308))
                                keyboard.doModal()
                                if keyboard.isConfirmed():
                                    keypassword = keyboard.getText()
                                if keypassword == None:
                                    return False   
                                ADDON.setSetting('user', value=keyemail)
                                ADDON.setSetting('pass', value=keypassword)
                                ADDON.setSetting(id='firstrun', value='true')
                                ADDON.setSetting(id='filmon', value='true')
                                dialog.ok(language(30021),language(30037), "",language(30038))    
                else: 
                        ADDON.setSetting(id='firstrun', value='true')
        r='http://www.filmon.com/api/group/%s?session_key=%s' % (url,ses)
        html = net.http_GET(r).content
        link = html.encode('ascii', 'ignore')
        data = json.loads(link, encoding='utf8')
        channels = data['channels']
        for field in data['channels']:
            url = field["id"]
            name = field["title"]
            icon = field["logo"]
            iconimage = str(icon).replace('/logo','/extra_big_logo')
            description = ''
            name = name.encode("utf-8")
            addDir(name,url,2,iconimage,description,'favorites','','','','tvguide','','')
            setView('episodes', 'default') 
            
    
def getStream(channels,resolution,watch_timeout):
    watch_timeout=str(watch_timeout)
    if resolution == '0':
        quality  = 'LOW'
        if len(watch_timeout)>5:
            quality  = 'HIGH'
    else:
        quality  = 'HIGH'

    for item in channels:
        if item['quality'].upper() == quality:
            return item
    return None 
     
                      
def FilmOn(url,iconimage):
        url='http://www.filmon.com/api/channel/%s?session_key=%s' % (url,ses)
        link = net.http_GET(url).content
        data = json.loads(link)
        channels= data['streams']
        watch_timeout= data['watch-timeout']
        stream = getStream(channels,resolution,watch_timeout)
        if stream is not None:
            foregex= stream['url']+'<'
            playpath=stream['name']
            name=stream['quality']
            if re.search('mp4:bc', link, re.IGNORECASE):
                    regex = re.compile('rtmp://(.+?)/(.+?)/<')
                    match = regex.search(foregex)
                    app = '%s/' %(match.group(2))
                    url= stream['url']+playpath
            if not re.search('mp4:bc', link, re.IGNORECASE):
                    regex = re.compile('rtmp://(.+?)/(.+?)/(.+?)id=([a-f0-9]*?)<')
                    match = regex.search(foregex)
                    app = '%s/%sid=%s' %(match.group(2), match.group(3),match.group(4))
                    url= stream['url']
            tcUrl=stream['url']
            swfUrl= 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf'
            pageUrl = 'http://www.filmon.com/'
            url= str(url)+' playpath='+str(playpath)+' app='+str(app)+' swfUrl='+str(swfUrl)+' tcUrl='+str(tcUrl)+' pageurl='+str(pageUrl)
            xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url)
            addLink(name,url,iconimage,'','','','','','','','')
            setView('movies', 'default') 
                        
                    
def MyRecordings(url):
        url='http://www.filmon.com/api/dvr-list?session_key=%s'%(ses)
        link = net.http_GET(url).content
        data = json.loads(link)
        recordings = data['recordings']
        for field in recordings:
            rec = field['id']
            name = field['title']
            desc = field['description']
            channel = field['channel_id']
            time = field['time_start']
            status = field['status']
            playPath = field['stream_name']
            url= field['stream_url']
            foregex = field['stream_url']+'<'
            regex = re.compile('rtmp://(.+?)/(.+?)/(.+?)/(.+?)/(.+?)/(.+?)/(.+?)<')
            match1 = regex.search(foregex)
            time=float(time)
            desc = desc.encode('utf-8')
            d=date.fromtimestamp(time).strftime("%d/%m/%Y")
            description='[B][%s][/B]\n%s'%(d,desc)
            iconimage='https://static.filmon.com/couch/channels/%s/extra_big_logo.png' % str(channel)
            try:
	            app = '%s/%s/%s/%s/%s/%s' %(match1.group(2), match1.group(3),match1.group(4),match1.group(5),match1.group(6),match1.group(7))
            except:
	            app = ''
            swfUrl= 'http://www.filmon.com/tv/modules/FilmOnTV/files/flashapp/filmon/FilmonPlayer.swf'
            pageUrl = 'http://www.filmon.com/my/recordings'
            url= str(url)+' playpath='+str(playPath)+' app='+str(app)+' swfUrl='+str(swfUrl)+' tcUrl='+str(url)+' pageurl='+str(pageUrl)
            if status=='Recorded':
	            status=language(30050)
	            name='%s %s' %(status,name)
	            name = name.encode('utf-8')
	            addLink(name,url,iconimage,description,'','','','delete','','',rec)
            if status=='Accepted':
	            status=language(30051)
	            name='%s %s' %(status,name)
	            name = name.encode('utf-8')
	            addLink(name,url,iconimage,description,'','','','delete','','',rec)
            if status=='Recording':
	            status=language(30052)
	            name='%s %s' %(status,name)
	            name = name.encode('utf-8')
	            addLink(name,url,iconimage,description,'','','','delete','','',rec)
            if status=='Failed':
	            status=language(30053)
	            name='%s %s' %(status,name)
	            name = name.encode('utf-8')
	            addLink(name,url,iconimage,description,'','','','delete','','',rec)
            setView('movies', 'epg')
                
                
def Record(url,programme_id,startdate_time):
        url ='http://filmon.com/api/dvr-add?session_key=%s&channel_id=%s&programme_id=%s&start_time=%s' % (ses,url,programme_id,startdate_time)
        link = net.http_GET(url).content
        try:
                
                if re.search('true',link ,re.IGNORECASE):
                        dialog = xbmcgui.Dialog()
                        dialog.ok(language(30021),language(30039),' ',language(30040))
                if re.search('false',link ,re.IGNORECASE):
                        dialog = xbmcgui.Dialog()
                        dialog.ok(language(30021),language(30041),' ',language(30042))
        except:
                dialog = xbmcgui.Dialog()
                dialog.ok(language(30021),language(3004),language(30043),language(30044))
                
def Delete(startdate_time):
        url='http://www.filmon.com/api/dvr-remove?session_key=%s&recording_id=%s'%(ses,startdate_time)
        try:
                link = net.http_GET(url).content
                if re.search('Task is removed',link ,re.IGNORECASE):
                        dialog = xbmcgui.Dialog()
                        dialog.ok(language(30021),language(30045),'',language(30046))
                else: 
                        dialog = xbmcgui.Dialog()
                        dialog.ok(language(30021),'',language(30047),'')
        except:
                dialog = xbmcgui.Dialog()
                dialog.ok(language(30021),'',language(30047),'')
                
def EPG(url,iconimage):
                url= 'http://www.filmon.com/api/channel/%s?session_key=%s' % (url,ses)
                link = net.http_GET(url).content
                data = json.loads(link)
                tvguide = data['tvguide']
                for field in tvguide:
                    programme_id= field["programme"]
                    startdate_time= field["startdatetime"] 
                    enddate_time= field["enddatetime"]
                    day= field["date_of_month"]                
                    cid= field["channel_id"]
                    desc= field["programme_description"] 
                    name= field["programme_name"]                
                    startdate_time_float=float(startdate_time) 
                    enddate_time_float=float(enddate_time) 
                    start=datetime.fromtimestamp(startdate_time_float)
                    end=datetime.fromtimestamp(enddate_time_float)
                    startdate_time_cleaned=start.strftime('%H:%M') 
                    enddate_time_cleaned=end.strftime('%H:%M')
                    name = '[%s %s] [B]%s[/B]'%(day,startdate_time_cleaned,name)
                    iconimage='http://static.filmon.com/couch/channels/%s/extra_big_logo.png'%(cid)
                    name = name.encode('utf-8')
                    description = desc.encode('utf-8')
                    url =str(cid)
                    addDir(name,url,2,iconimage,description,'','','record','','',programme_id,startdate_time)
                    setView('movies', 'epg') 
                    
def channel_dict(url):
    r='http://www.filmon.com/api/channel/%s?session_key=%s'%(url,ses)
    link = net.http_GET(r).content
    data=json.loads(link)
    name=data['title']
    name=name.encode('utf-8')
    return name

def FAV(url):
    grp='http://www.filmon.com/api/favorites?session_key=%s&run=get'% (ses)
    link = net.http_GET(grp).content
    data=json.loads(link)
    result=data['result']
    for field in result:
        url=field['channel_id']
        iconimage='http://static.filmon.com/couch/channels/%s/extra_big_logo.png'%(url)
        name=channel_dict(url)
        addDir(name,url,2,iconimage,'','','delete','','','tvguide','','')
        setView('movies', 'default') 
                
def favourite(url):
    dialog = xbmcgui.Dialog()
    grp='http://www.filmon.com/api/favorites?session_key=%s&channel_id=%s&run=add'%(ses,url)
    link = net.http_GET(grp).content
    dialog.ok(language(30021),language(30048),' ','')  

def deletefavourite(url):
    dialog = xbmcgui.Dialog()
    grp='http://www.filmon.com/api/favorites?session_key=%s&channel_id=%s&run=remove'%(ses,url)
    link = net.http_GET(grp).content
    dialog.ok(language(30021),language(30049),' ','')  
                
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

        
def addDir(name,url,mode,iconimage,description, favorites, deletefav, record, deleterecord, tvguide,programme_id,startdate_time):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)+"&programme_id="+urllib.quote_plus(programme_id)+"&startdate_time="+urllib.quote_plus(startdate_time)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":description} )
        menu = []
        if favorites:
              menu.append((language(30054),'XBMC.RunPlugin(%s?name=None&url=%s&mode=10&iconimage=None&description=None)'%(sys.argv[0],url)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if deletefav:
              menu.append((language(30055),'XBMC.RunPlugin(%s?name=None&url=%s&mode=11&iconimage=None&description=None)'%(sys.argv[0],url)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if record:
              menu.append((language(30056),'XBMC.RunPlugin(%s?name=None&url=%s&mode=6&iconimage=None&description=None&programme_id=%s&startdate_time=%s)'%(sys.argv[0],url,programme_id,startdate_time)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if deleterecord:
              menu.append((language(30057),'XBMC.RunPlugin(%s?name=None&url=None&mode=7&iconimage=None&description=None&startdate_time=%s)'%(sys.argv[0],startdate_time)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if tvguide:
              menu.append((language(30058),'XBMC.Container.Update(%s?name=None&url=%s&mode=8&iconimage=%s&description=None)'%(sys.argv[0],url,iconimage)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok   
                     
def addLink(name,url,iconimage,description, favorites, deletefav, record, deleterecord,tvguide,programme_id,startdate_time):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty("IsPlayable","true")
        menu = []
        if favorites:
              menu.append((language(30054),'XBMC.RunPlugin(%s?name=None&url=%s&mode=10&iconimage=None&description=None)'%(sys.argv[0],url)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if deletefav:
              menu.append((language(30055),'XBMC.RunPlugin(%s?name=None&url=%s&mode=11&iconimage=None&description=None)'%(sys.argv[0],url)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if record:
              menu.append((language(30056),'XBMC.RunPlugin(%s?name=None&url=%s&mode=6&iconimage=None&description=None&pid=%s&st=%s)'%(sys.argv[0],url,programme_id,startdate_time)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        if deleterecord:
              menu.append((language(30057),'XBMC.RunPlugin(%s?name=None&url=None&mode=7&iconimage=None&description=None&startdate_time=%s)'%(sys.argv[0],startdate_time)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
              
        if tvguide:
              menu.append((language(30058),'XBMC.Container.Update(%s?name=None&url=%s&mode=8&iconimage=%s&description=None)'%(sys.argv[0],url,iconimage)))
              liz.addContextMenuItems(items=menu, replaceItems=True)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=False)
        return ok 
        
def setView(content, viewType):
        # set content type so library shows more views and info
        if content:
                xbmcplugin.setContent(int(sys.argv[1]), content)
        if ADDON.getSetting('auto-view') == 'true':
                xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )
                
        
params=get_params()
url=None
name=None
mode=None
iconimage=None
description=None
favorites=None 
deletefav=None
record=None
deleterecord=None
programme_id=None
startdate_time=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        description=urllib.unquote_plus(params["description"])
except:
        pass
try:        
        programme_id=urllib.unquote_plus(params["programme_id"])
except:
        pass
try:        
        startdate_time=urllib.unquote_plus(params["startdate_time"])
except:
        pass
        

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "IconImage: "+str(iconimage)
   
        

if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
        
elif mode==2:
        print ""+url
        FilmOn(url,iconimage)
        
elif mode==3:
        print ""+url
        Channels(name,url)
        
elif mode==4:
        print ""+url
        Channel_Lists(url)
        
elif mode==5:
        print ""+url
        MyRecordings(url)
        
elif mode==6:
        print ""+url
        Record(url,programme_id,startdate_time)
        
elif mode==7:
        print ""+url
        Delete(startdate_time)
        
elif mode==8:
        print ""+url
        EPG(url,iconimage)
        
elif mode==9:
        print ""+url
        FAV(url)
        
elif mode==10:
        print ""+url
        favourite(url)
        
elif mode==11:
        print ""+url
        deletefavourite(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))

