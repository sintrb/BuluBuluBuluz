# -*- coding: UTF-8 -*
'''
Created on 2014-4-9

@author: RobinTang
'''
from sinlibs.tools import ynulib
from sinlibs.utils import timeutils 
import time
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



def runtest(cxt):
    if not 'reuslts' in cxt:
        cxt['reuslts'] = []
    if not 'testindex' in cxt:
        cxt['testindex'] = 0
    
    if cxt['testindex'] >= len(testlist):
        keys = ['name', 'cost', 'result', 'start']
        mail = '\n----\n'.join(['\n'.join(['%s:%s'%(k,tr[k]) for k in keys]) for tr in cxt['reuslts']])
        cxt['reuslts'] = []
        cxt['testindex'] = 0
        return mail
    else:
        test = testlist[cxt['testindex']]
        sttime = time.time()
        okflag = test.runtest()
        edtime = time.time()
        oftime = edtime-sttime
        cxt['reuslts'].append(
                              {
                               'name':test.name,
                               'cost':oftime,
                               'result':okflag,
                               'start':timeutils.stamp2str(sttime)
                               }
                              )
        cxt['testindex'] = cxt['testindex'] + 1
        return None



if __name__ == '__main__':
    cxt = {}
    print runtest(cxt)
    print runtest(cxt)
    print runtest(cxt)




