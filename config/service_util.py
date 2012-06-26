import pystache, os, getpass

file_path = os.path.realpath(__file__)

lr_base = os.path.normpath(os.path.join(os.path.dirname(file_path), ".."))

virt_env_var = "$VIRTUAL_ENV"



def_context = {
    "LR_BASE": lr_base,
    "LR_USER": getpass.getuser(),
    "LR_GRP": getpass.getuser(),
    "VAR_DIR" : "/var"
}

virtualenv = os.path.expandvars(virt_env_var)
if virtualenv != virt_env_var and len(virtualenv) > 0:
    def_context["LR_VIRTUALENV"] = virtualenv


def checkFileExists(userInput):
    try:
       with open(userInput) as f: pass
    except IOError as e:
       return False
    return True

def checkDirectoryExists(userInput):
    return os.path.isdir(userInput)

def getFirstValidDefaultFromList(items, validate):
    for item in items:
        if validate(item):
            return item
    return items[0]


def prompt():
    import setup_utils
    context = {}
    context.update(def_context)

    context["LR_BASE"] = setup_utils.getInput("Base Learning Registry Directory", context["LR_BASE"], checkDirectoryExists)

    possible = [
        "/var",
        "/usr/local/var"
    ]

    context["VAR_DIR"] = setup_utils.getInput("var directory", getFirstValidDefaultFromList(possible, checkDirectoryExists), checkDirectoryExists)


    context["LR_USER"] = setup_utils.getInput("Enter the user that LR process will run as", context["LR_USER"])
    context["LR_GRP"] = setup_utils.getInput("Enter the group that LR process will run as", context["LR_GRP"])

    return context




start_stop_template = '''#! /bin/bash
# /etc/init.d/learningregistry
#

LR_HOME={{LR_BASE}}/LR
LR_USER={{LR_USER}}
LR_GRP={{LR_GRP}}
LR_VIRTUALENV={{LR_VIRTUALENV}}
LR_PID_DIR={{VAR_DIR}}/run/learningregistry
LR_LOG_DIR={{VAR_DIR}}/log/learningregistry

LR_PID=$LR_PID_DIR/uwsgi.pid
LR_LOG=$LR_LOG_DIR/uwsgi.log

# Some things that run always
if [ ! -e $LR_PID_DIR ]
then
    mkdir -p $LR_PID_DIR
    chown $LR_USER:$LR_GRP $LR_PID_DIR
fi

if [ ! -e $LR_LOG_DIR ]
then
    mkdir -p $LR_LOG_DIR
    chown $LR_USER:$LR_GRP $LR_LOG_DIR
fi

lr_start () {
    if [ -e $LR_PID ]
    then
        echo "LR Node is already running"
        exit 1
    fi

    su $LR_USER -c "{{#LR_VIRTUALENV}}source $LR_VIRTUALENV/bin/activate; {{/LR_VIRTUALENV}}uwsgi --ini-paste $LR_HOME/development.ini start {{#LR_VIRTUALENV}}-H $LR_VIRTUALENV{{/LR_VIRTUALENV}} --pidfile $LR_PID --daemonize $LR_LOG{{#LR_VIRTUALENV}}; deactivate{{/LR_VIRTUALENV}}"
    echo "LR Node is starting. Log: $LR_LOG   PID: $LR_PID"
}

lr_stop () {
    if [ -e $LR_PID ]
    then
        su $LR_USER -c "{{#LR_VIRTUALENV}}source $LR_VIRTUALENV/bin/activate; {{/LR_VIRTUALENV}}uwsgi --stop $LR_PID;rm -f $LR_PID{{#LR_VIRTUALENV}}; deactivate{{/LR_VIRTUALENV}}"
        echo "LR Node is stopping. Log: $LR_LOG   PID: $LR_PID"
    fi

}

lr_restart () {
    if [ -e $LR_PID ]
    then
        su $LR_USER -c "{{#LR_VIRTUALENV}}source $LR_VIRTUALENV/bin/activate; {{/LR_VIRTUALENV}}uwsgi --stop $LR_PID;rm -f $LR_PID"
        su $LR_USER -c "{{#LR_VIRTUALENV}}source $LR_VIRTUALENV/bin/activate; {{/LR_VIRTUALENV}}uwsgi --ini-paste $LR_HOME/development.ini start {{#LR_VIRTUALENV}}-H $LR_VIRTUALENV{{/LR_VIRTUALENV}} --pidfile $LR_PID --daemonize $LR_LOG{{#LR_VIRTUALENV}}; deactivate{{/LR_VIRTUALENV}}"
        echo "LR Node is restarting. Log: $LR_LOG   PID: $LR_PID"
    fi

}


# Carry out specific functions when asked to by the system
case "$1" in
    start)
        echo "Starting script learningregistry "
        lr_start
        ;;
    stop)
        echo "Stopping script learningregistry"
        lr_stop
        ;;
    restart)
        echo "Restarting script learningregistry"
        lr_restart
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
'''


if __name__ == "__main__":
    # print file_path
    # print __file__
    # print lr_base
    context = prompt()

    contents =  pystache.render(start_stop_template, context)
    with open("learningregistry.sh", "w") as f:
        f.truncate(0)
        f.flush()
        f.write(contents)
        f.close()

    print("###########################################################")
    print("## Learning Registry Start/Stop Script\n")

    print("##")
    print("###########################################################")
    print("## Written to learningregistry.sh")
    print("## You should copy this file to /etc/init.d/learningregistry")
