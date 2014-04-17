# -*- coding: UTF-8 -*
'''
Created on 2014-4-9

@author: RobinTang
'''
from sinlibs.tools import ynulib
from sinlibs.utils import timeutils 
import time
import json
class Test:
    def __init__(self, name):
        self.name = name
    def runtest(self):
        raise Exception('Unoverride this method')

class YnuLibTest(Test):
    def __init__(self):
        Test.__init__(self, 'YnuLib Test')
    def runtest(self):
        return len(ynulib.search_books('OK'))>0



testlist = [
            YnuLibTest()
            ]



def runtest(kvdb):
    if not 'reuslts' in kvdb:
        kvdb['reuslts'] = []
    if not 'testindex' in kvdb or kvdb['testindex'] == None:
        kvdb['testindex'] = 0
    testindex = 0 if kvdb['testindex']==None else kvdb['testindex']
    

    if testindex >= len(testlist):
        keys = ['name', 'cost', 'result', 'start', 'message']
        mail = '\n----\n'.join(['\n'.join(['%s:%s'%(k,tr[k]) for k in keys]) for tr in kvdb['reuslts']])
        kvdb['reuslts'] = []
        kvdb['testindex'] = 0
        return mail
    else:
        test = testlist[testindex]
        sttime = time.time()
        okflag = test.runtest()
        edtime = time.time()
        oftime = edtime-sttime
        tres = {
                 'name':test.name,
                 'cost':oftime,
                 'result':okflag,
                 'start':timeutils.stamp2str(sttime),
                 'message':okflag
                 }
        result = kvdb['reuslts']
        result.append(tres)
        kvdb['reuslts'] = result
        kvdb['testindex'] = testindex + 1
        return json.dumps(tres)



if __name__ == '__main__':
    cxt = {}
    print runtest(cxt)
    print runtest(cxt)




