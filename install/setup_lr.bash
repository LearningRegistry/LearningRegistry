#!/usr/bin/env bash

# Written by: Ali Asad Lotia <lotia@umich.edu>

# This script automates the installation of the software required to
# set up a Learning Registry node for development.

# It installs CouchDB and also installs the python dependencies for
# Learning Registry in a virtualenv using pip. The only argument
# accepted is the name of a virtualenv, if no argument is supplied and
# one by the the default "lr" name doesn't already exist, the
# virtualenv is created. If it exists, the script exits indicating
# that the destination directory already exists.

# Usage
# ./setup_lr.bash [name of virtualenv]
# Note: the name of the virtualenv is optional.

# Please DON'T invoke this script as root or sudo. It will prompt you
# for your password if you need to sudo something.

# This script should work with Ubuntu 10.04 onwards and MacOS 10.6.x

# It requires the Homebrew package manager on MacOS. See
# https://github.com/mxcl/homebrew for further information.

# The comments are somewhat verbose. Apologies if that annoys you.

# set options to keep this script well behaved. Consult the bash
# manual for more detail.
set -o errexit # exit if an error is returned outside a loop or conditional.
set -o nounset # exit if attempting to access an unset variable
set -o pipefail # exit if any part of a pipe fails

THIS_SCRIPT_DIR=${PWD}

UBUNTU_LR_DEPS="build-essential libxml2-dev libxslt1-dev python-dev python-virtualenv curl autotools-dev automake autoconf"
UBUNTU_MIN_VER="10.04"

COUCHONE_x86_64_DOWNLOAD_URL="http://c3145442.r42.cf0.rackcdn.com/couchbase-server-community_x86_64_1.1.deb"

COUCHONE_x86_DOWNLOAD_URL="http://c3145442.r42.cf0.rackcdn.com/couchbase-server-community_x86_1.1.deb"

COUCHONE_DOWN_DIR="${HOME}"

COUCH_DEF_PORT=5984

ARCH=$(uname -m)

# check to see if we are running as root or sudo, and stop if you are.
if [[ $(whoami) == 'root' ]] ; then
    echo "Please don't run this script as root or using sudo." >&2
    echo "It's generally not a good idea to create python virtualenvs as root or sudo." >&2
    echo "You may require sudo privileges but shouldn't run the script as sudo." >&2
    exit 1
fi

echo "========================================================================"
echo "This script will install the software to set up a Learning Registry node"
echo "for development."
echo "========================================================================"

function wait_before_proceeding () {
    local i=$1

    echo "Waiting ${i} seconds before proceeding."
    echo "Hit Control-C to exit without installing."
    while [[ $i -gt 0 ]]
    do
        echo "Proceeding in $i seconds."
        sleep 1
        i=$((${i} - 1))
    done
}

wait_before_proceeding 3

function missing_binary_bail () {
    echo -n "${1} was not found, aborting."
    echo "Please install ${1} before running this script." >&2
    exit 1
}

# The Linux distro verification is a bit Ubuntu centric. Would be nice
# to abstract it some more so support for other distros is easier to
# add.
function check_distro () {
    local LSB_REL_PATH=$(type -P "lsb_release") || {
        missing_binary_bail "lsb_release"
    }

    local DIST_NAME=$(lsb_release -is)

    if [[ "${DIST_NAME}" != "Ubuntu" ]] ; then
        echo "The only Linux distribution currently supported is Ubuntu." >&2
        exit 1
    fi

    local DIST_VER=$(lsb_release -rs)

    if [[ ${DIST_VER%%.*} -lt ${UBUNTU_MIN_VER%%.*} ]] ; then
        echo "Ubuntu ${DIST_VER} is too old. We support ${UBUNTU_MIN_VER} onwards." >&2
        exit 1
    fi
}

function can_sudo () {
    local GROUP_LIST=$(groups) || {
        echo "Unable to determine group membership for ${USER}. Exiting." >&2
        exit 1
    }

    local IN_ADMIN_GROUP=$(awk -v group_list="${GROUP_LIST}" -v admin_group="admin" \
        'BEGIN { print index(group_list, admin_group) }') || {
        echo "Can't determine if ${USER} is an administrator. Exiting."
        exit 1
    }

    if [[ ${IN_ADMIN_GROUP} -eq 0 ]] ; then
        echo "You must be an admin user to run this script." >&2
        exit 1
    fi
}

function install_couch_ubuntu () {

    local COUCH_DOWN_URL=""

    echo "Downloading CouchOne Community Edition to ${HOME}."
    cd "${HOME}" || {
        echo "Couldn't change to ${HOME} directory. This is very odd." >&2
        echo "Figure out why you can't write to your own home directory and re-run this scipt!" >&2
        echo "Exiting."
        exit 1
    }

    # detect architecture and specify download URL correctly
    if [[ "${ARCH}" == "x86_64" ]] ; then
	COUCH_DOWN_URL="${COUCHONE_x86_64_DOWNLOAD_URL}"
    elif [[ "${ARCH}" == "i386" ]] || [[ "${ARCH}" == "i686" ]] ; then
	COUCH_DOWN_URL="${COUCH_x86_DOWNLOAD_URL}"
    else
	# In this case, Couch One isn't available for the current architecture.
	echo "There is no Couch One installer available for your architecture."
	exit 1
    fi

    # check return state of all below and quit if they don't complete
    wget "${COUCH_DOWN_URL}" || {
        echo "Could not download CouchDB. Exiting."
        exit 1
    }

    sudo dpkg --install ${COUCHONE_DOWN_URL##*/}
    cd "${THIS_SCRIPT_DIR}"
}

# This function should be refactored so other distributions can easily
# use the output strings.
function install_deps_ubuntu () {
    can_sudo
    if netcat -z localhost ${COUCH_DEF_PORT} ; then
        echo "CouchDB (or something else) is already running on ${COUCH_DEF_PORT}."
        echo "We won't attempt to install CouchDB."
    else
        install_couch_ubuntu
    fi

    echo "Installing requirements to build LR Python packages and test LR."

    sudo apt-get install -y ${UBUNTU_LR_DEPS}
    # Check if required stuff is in our path
    (type -P "python") || {
        missing_binary_bail "python"
    }

    (type -P "pip") || {
        missing_binary_bail "pip"
    }

    (type -P "virtualenv") || {
        missing_binary_bail "virtualenv"
    }

    (type -P "cc") || {
        missing_binary_bail "gcc"
    }
}

function install_deps_osx () {
    (type -P "cc") || {
        missing_binary_bail "Xcode"
    }

    # Check to see if we can write to the directory where the missing
    # python tools will be installed.
    local DEF_INST_PREFIX="/usr/local"
    local MUST_SUDO=0

    if [[ ! -w "${DEF_INST_PREFIX}" ]] ; then
        MUST_SUDO=1
    fi

     # check to see if Homebrew is installed. Print out information on
     # installation if it isn't found.
    (type -P "brew") || {
        echo "Hombrew isn't installed."
        echo "Go to https://github.com/mxcl/homebrew for installation info." >&2
        exit 1
    }

     # install pip
    if !(type -P "pip") ; then
        echo "Installing pip."
        if [[ ${MUST_SUDO} -eq 0 ]] ; then
            easy_install pip
        elif [[ ${MUST_SUDO} -eq 1 ]] ; then
            sudo easy_install pip
        fi
    else
        echo "pip appears to be installed. Make sure you have a current version."
    fi

     # install virtualenv
    if !(type -P "virtualenv") ; then
        echo "Installing virtualenv."
        if [[ ${MUST_SUDO} -eq 0 ]] ; then
            pip install virtualenv
        elif [[ ${MUST_SUDO} -eq 1 ]] ; then
            sudo pip install virtualenv
        fi
    else
        echo "Virtualenv appears to be installed, make sure you have a current version."
    fi

    # install couchdb. should we also check to see if it's running on MacOS?
    if !(type -P couchdb) ; then
        echo "Installing couchdb. This may take a while."
        if [[ ! -w $(dirname $(dirname $(type -P "brew")))"/Cellar" ]] ; then
            sudo brew install couchdb
        else
            brew install couchdb
        fi
    else
        echo "CouchDB appears to be installed."
        echo "Learning Registry has currently been tested on CouchDB 1.0.2."
        echo "Make sure you have that version or newer."
    fi
}

# Determine OS
case "${OSTYPE}"  in
    "linux-gnu")
        echo "Running on Linux, determining distribution."
        check_distro
        install_deps_ubuntu
        ;;
    "darwin10.0")
        echo  "Running on MacOS 10.6.x."
        echo "Attempting install of dependencies."
        install_deps_osx
        ;;
esac

echo
echo "========================================================================"
echo "All the requirements other than python packages should now be installed."
echo "========================================================================"
echo

# Set the name of the virtualenv if one is specified. We do no
# sanitization of the passed value. Fragile stuff here.
if [[ $# -gt 0 ]] ; then
    bash ./install_pydeps.bash "${1}"
else
    bash ./install_pydeps.bash
fi
