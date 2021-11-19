#!/usr/bin/python

import requests
import time
import hashlib
import os
from requests.cookies import create_cookie
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    os.mkdir('notes')
except OSError:
    print OSError

def timestamp():
    return str(int(time.time() * 1000))

class YoudaoNoteSession(requests.Session):
    def __init__(self):
        requests.Session.__init__(self)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Aoyou/I05jDV9aSW5BZSJoWgpsRPl9TdwkNT6NGbhU-qFKg54hwlMWpPK_5Rgxfw==',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en,zh-CN;q=0.9,zh;q=0.8'
        }

    def login(self, username, password):
        self.get('https://note.youdao.com/web/')

        self.headers['Referer'] = 'https://note.youdao.com/web/'
        self.get('https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web')

        self.headers['Referer'] = 'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web'
        self.get('https://note.youdao.com/login/acc/pe/getsess?product=YNOTE&_=' + timestamp())
        self.get('https://note.youdao.com/auth/cq.json?app=web&_=' + timestamp())
        self.get('https://note.youdao.com/auth/urs/login.json?app=web&_=' + timestamp())
        data = {
            "username": username,
            "password": hashlib.md5(password).hexdigest()
        }
        self.post('https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=urstoken&cf=6&fr=1&systemName=&deviceType=&ru=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&er=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vcode=&systemName=&deviceType=&timestamp=' + timestamp(), data=data, allow_redirects=True)
        self.get('https://note.youdao.com/yws/mapi/user?method=get&multilevelEnable=true&_=' + timestamp())
        print(self.cookies)
        self.cstk = self.cookies.get('YNOTE_CSTK')

    def getRoot(self):
        data = {
            'path': '/',
            'entire': 'true',
            'purge': 'false',
            'cstk': self.cstk
        }
        response = self.post('https://note.youdao.com/yws/api/personal/file?method=getByPath&keyfrom=web&cstk=%s' % self.cstk, data = data)
        print('getRoot:' + response.content)
        jsonObj = json.loads(response.content)
        return jsonObj['fileEntry']['id']

    def getNote(self, id, saveDir, name):
        data = {
            'fileId': id,
            'version': -1,
            'convert': 'true',
            'editorType': 1,
            'cstk': self.cstk
        }
        url = 'https://note.youdao.com/yws/api/personal/sync?method=download&keyfrom=web&cstk=%s' % self.cstk
        response = self.post(url, data = data)
        with open(r'%s/%s.xml' % (saveDir, name), 'w') as fp:
            fp.write(response.content)

    def getNoteDocx(self, id, saveDir, name):
        url = 'https://note.youdao.com/ydoc/api/personal/doc?method=download-docx&fileId=%s&cstk=%s&keyfrom=web' % (id, self.cstk)
        response = self.get(url)
        with open(r'%s/%s.docx' % (saveDir, name), 'w') as fp:
            fp.write(response.content)


    def getFileRecursively(self, id, saveDir, doc_type):
        data = {
            'path': '/',
            'dirOnly': 'false',
            'f': 'false',
            'cstk': self.cstk
        }
        url = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s' % (id, self.cstk)
        lastId = None
        count = 0
        total = 1
        while count < total:
            if lastId == None:
                response = self.get(url)
            else:
                response = self.get(url + '&lastId=%s' % lastId)
            print('getFileRecursively:' + response.content)
            try:
                jsonObj = json.loads(response.content)
            except Exception as e:
                with open(r'error_log.txt', 'a+') as fp:
                    fp.write('error jsonObj: '+e+'\n')
            total = jsonObj['count']
            for entry in jsonObj['entries']:
                fileEntry = entry['fileEntry']
                id = fileEntry['id']
                name = fileEntry['name']
                print('%s  %s/%s' % (id,saveDir,name))
                if fileEntry['dir']:
                    subDir = saveDir + '/' + name
                    try:
                        os.lstat(subDir)
                    except OSError:
                        os.mkdir(subDir)
                    self.getFileRecursively(id, subDir, doc_type)
                else:
                    try:
                        #with open('%s/%s.json' % (saveDir, name), 'w') as fp:
                        #    fp.write(json.dumps(entry,ensure_ascii=False).encode('utf-8'))
                        if doc_type == 'xml':
                            self.getNote(id, saveDir, name)
                        # docx word
                        else: 
                            if name.endswith('.note'):
                                self.getNoteDocx(id, saveDir, name.replace("/", " "))
                    except OSError:
                        with open(r'error_log.txt', 'a+') as fp:
                            fp.write(id+'\n')
                            fp.write(name+'\n')
                            fp.write(OSError+'\n')
                count = count + 1
                lastId = id

    def getAll(self, saveDir, doc_type):
        rootId = self.getRoot()
        self.getFileRecursively(rootId, saveDir, doc_type)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('args: <username> <password> [saveDir [doc_type]]' )
        print('doc_type: xml or docx')
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    if len(sys.argv) >= 4: 
        saveDir = sys.argv[3]
    else:
        saveDir = '.'
    if len(sys.argv) >= 5:
        doc_type = sys.argv[4]
    else:
        doc_type = 'xml'
    sess = YoudaoNoteSession()
    sess.login(username, password)
    sess.getAll(saveDir, doc_type)
