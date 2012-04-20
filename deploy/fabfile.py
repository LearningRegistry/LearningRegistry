from fabric.api import env, run
def dev():
    env.hosts = ['lrdev01.learningregistry.org',
                 'lrdev02.learningregistry.org']    

def sandbox():
    env.hosts = ['sandbox.learningregistry.org']

def alpha():
    env.hosts = ['alpha.learningregistry.org']
    
def prod():    
    env.hosts = ['node01.public.learningregistry.net',
                 'node03.public.learningregistry.net',
                 'node03.public.learningregistry.net']

def deploy(branch, runTests=False):
    activateLrVirtualEnv = '. ~/virtualenv/lr/bin/activate'
    changeToLRProjectDir = 'cd ~/gitrepos/LearningRegistry/LR'
    deactivate = 'deactivate'
    gitCheckout = ['cd ~/gitrepos/LearningRegistry',
                   'git checkout master',
                   'git pull',
                   'git checkout origin/%s' % branch]
    updateLRInstall = [activateLrVirtualEnv,
                       changeToLRProjectDir,
                       'yes | pip uninstall LR',
                       'yes | pip install .',
                       'yes | pip install uwsgi',
                       deactivate]
    startLRServer = [activateLrVirtualEnv,
                     changeToLRProjectDir,
                     'uwsgi --ini-paste development.ini --virtualenv ~/virtualenv/lr/ --daemonize uwsgi.log --pidfile uwsgi.pid',
                     deactivate]
    testCommand = ['. ~/virtualenv/lr/bin/activate',
                   'cd ~/gitrepos/LearningRegistry/LR',
                   'nosetests lr/tests/functional/test_harvest.py',
                   'nosetests lr/tests/functional/test_obtain.py',
                   'nosetests lr/tests/functional/test_OAI-OMH.py',
                   'nosetests lr/tests/functional/test_slice.py']                     
    run(';'.join(gitCheckout))
    run(';'.join(updateLRInstall))
    #run('killall -9 uwsgi;')
    if runTests:
        run(';'.join(testCommand))
    run('service learningregistry restart')
