from fabric.api import env, run
def dev():
    env.hosts = ['lrdev01.learningregistry.org',
                 'lrdev02.learningregistry.org']    

def test():
    env.hosts = ['lrtest01.learningregistry.org',
                 'lrtest02.learningregistry.org']
def prod():    
    env.hosts = ['node01.public.learningregistry.net',
                 'node03.public.learningregistry.net',
                 'node03.public.learningregistry.net']

def deploy(username, password, branch, runTests=False):
    env.user = username
    env.password = password
    run('cd ~/gitrepos/LearningRegistry;git checkout master;git pull;git checkout origin/%s;' % branch)
    run('. ~/virtualenv/lr/bin/activate;cd ~/gitrepos/LearningRegistry/LR;pip uninstall LR;yes | pip -q install .;yes | pip install -q uwsgi;')
    run('killall -9 uwsgi;')
    if runTests:
        testCommand = '. ~/virtualenv/lr/bin/activate;'
        testCommand += 'cd ~/gitrepos/LearningRegistry/LR;'
        testCommand += 'nosetests lr/tests/functional/test_harvest.py;'
        testCommand += 'nosetests lr/tests/functional/test_obtain.py;'
        testCommand += 'nosetests lr/tests/functional/test_OAI-OMH.py;'
        testCommand += 'nosetests lr/tests/functional/test_slice.py;'
        run(testCommand)
    run('. ~/virtualenv/lr/bin/activate;cd ~/gitrepos/LearningRegistry/LR/;uwsgi --ini-paste development.ini --virtualenv ~/virtualenv/lr/ --daemonize uwsgi.log --pidfile uwsgi.pid;deactivate;')
