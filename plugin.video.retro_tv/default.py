#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin, xbmcgui, sys, urllib, urllib2, re, xbmcaddon, socket, HTMLParser
socket.setdefaulttimeout(30)
thisPlugin = int(sys.argv[1])

settings = xbmcaddon.Addon(id='plugin.video.retro_tv')
translation = settings.getLocalizedString
userAgentString = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16'
htmlp = HTMLParser.HTMLParser()
def index():
    addDir(translation(30003), 'http://www.retro-tv.de/archiv')
    addDir(translation(30004), 'http://www.retro-tv.de/sendungsliste', 3)
    addDir(translation(30002), '', 4)
    xbmcplugin.endOfDirectory(thisPlugin)
def listFolgen(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', userAgentString)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile(' <td><a title="([^"]+)" href="([^"]+)"><img src="[^"]*?image=([^"]+)"></a>', re.MULTILINE|re.DOTALL).findall(link)
    for name,url,thumbnail in match:
	addLink(htmlp.unescape(name), 'http://www.retro-tv.de/' + url, 2, 'http://www.retro-tv.de/' + urllib.unquote_plus(thumbnail))
    match=re.compile('<li><a title="Seite \d+" href="[^"]+" class="blaettern_active">\d+</a><li><a title="([^"]+)" href="([^"]+)" >\d+</a>').findall(link)
    for name,url in match:
        addDir(translation(30001), url)
    xbmcplugin.endOfDirectory(thisPlugin)
def playVideo(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', userAgentString)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<source id=video-html5-source src="([^"]+)" type="video/mp4" />').findall(link)
    for url in match:
	listitem = xbmcgui.ListItem(path=url)
    return xbmcplugin.setResolvedUrl(thisPlugin, True, listitem)
def listThemen(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', userAgentString)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<a href="([^"]+)" title="([^"]+)"><img  alt="[^"]+" src="([^"]+)"></a>').findall(link)
    for url,name,thumbnail in match:
	addLink(htmlp.unescape(name), 'http://www.retro-tv.de/' + url, 2, htmlp.unescape(thumbnail))
    xbmcplugin.endOfDirectory(thisPlugin)
def search():
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        req = urllib2.Request('http://www.retro-tv.de/sendungsliste')
        req.add_header('User-Agent', userAgentString)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<a href="([^"]+)" title="([^"]+)"><img  alt="[^"]+" src="([^"]+)"></a>').findall(link)
        for url,name,thumbnail in match:
            if name.lower().find(keyboard.getText().lower()) > -1:
                addLink(htmlp.unescape(name), 'http://www.retro-tv.de/' + url, 2, 'http://www.retro-tv.de/' + htmlp.unescape(thumbnail))
        xbmcplugin.endOfDirectory(thisPlugin)
    
def addLink(name, url, mode=1, iconimage='', description='', isVideo=True):
    u    = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
    ok   = True
    icon = 'DefaultVideo.png'
    if (not isVideo):
        icon = 'DefaultAudio.png'
    liz  = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ 'Title': name, 'Plot': description, 'Director': 'Henning Harperath/Paddy Kroetz' } )
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok
def addDir(name, url, mode=1, iconimage=''):
    u   = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode)
    ok  = True
    liz = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ 'Title': name })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
def parameters_string_to_dict(parameters):
    """Convert parameters encoded in a URL to a dict."""
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split('&')
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)
if mode == "1":
    listFolgen(url)
elif mode == "2":
    playVideo(url)
elif mode == "3":
    listThemen(url)
elif mode == "4":
    search()
else:
    index()