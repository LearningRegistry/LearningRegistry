#!/usr/bin/env bash

# Written by: Ali Asad Lotia <lotia@umich.edu>

# This script installs the python packages required to run a Learning
# Registry node in a virtualenv using pip.

# The only argument accepted is the name of a virtualenv, if no
# argument is supplied and one by the the default "lr" name doesn't
# already exist, the virtualenv is created. If it exists, the script
# exits indicating that the destination directory already exists.

# Usage
# ./install_pydeps.bash [name of virtualenv]
# Note: the name of the virtualenv is optional.

# This script should work most places a compiler, python including
# headers and virtualenv are available.

# The comments are somewhat verbose. Apologies if that annoys you.

# set options to keep this script well behaved. Consult the bash
# manual for more detail.
set -o errexit # exit if an error is returned outside a loop or conditional.
# set -o nounset # exit if attempting to access an unset variable. useful when writing scripts
set -o pipefail # exit if any part of a pipe fails

# TODO, should we check for distutils configuration files, or is that
# a spectacularly high level of paranoia/yak shaving?

# The default name for the virtualenv.
LR_ENV_NAME="lr"

echo
echo "========================================================================"
echo "This script will install the python packages to a virtualenv."
echo "It requires:"
echo "C/C++ compilers"
echo "Python including header files"
echo "pip"
echo "virtualenv"
echo "========================================================================"
echo

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

# Check if required stuff is in our path
PYTHON_PATH=$(type -P "python")
PIP_PATH=$(type -P "pip")
VIRTUALENV_PATH=$(type -P "virtualenv")
CC_PATH=$(type -P "cc")


# hints for this function provided at
# http://stackoverflow.com/questions/874389/bash-test-for-a-variable-unset-using-a-function
function check_if_present () {
    if [[ ! "${!1}" ]] ; then
        echo "${2} was not found, aborting. Please install ${2} before running this script." >&2
        exit 1
    fi
}

# parsing xcodebuild -version output largely lifted from
# http://trac.sagemath.org/sage_trac/attachment/ticket/11280/trac_11280_xcode4unsupported.patch
function get_xcode_version () {
    XCODE_VER=$(xcodebuild -version | grep Xcode | sed 's/[A-Za-z]//g;s/^[ \t]*//;s/[ \t]*$//;')
}

# Set the name of the virtualenv if one is specified. We do no
# sanitization of the passed value nor do we do much sanity checking
# for paths outside the current user's home.
if [[ $# -gt 0 ]] ; then
    LR_ENV_NAME="${1}"
fi

PIP_ENV="${LR_ENV_NAME}"

# check if LR_ENV_NAME contains a directory separator
LR_ENV_NAME_IS_DIR=$(awk -v env_name="${LR_ENV_NAME}" -v path_sep="/" \
    'BEGIN { print index(env_name, path_sep) }')

check_if_present CC_PATH "c/c++ compiler"
check_if_present PYTHON_PATH "python" # how do we check for header files?
check_if_present PIP_PATH "pip"
check_if_present VIRTUALENV_PATH "virtualenv"

echo "Found c compiler at: ${CC_PATH}"
echo "Found python at: ${PYTHON_PATH}"
echo "Found pip at: ${PIP_PATH}"
echo "Found virtualenv at: ${VIRTUALENV_PATH}"

# If virtualenvwrapper is set up, passing a directory path as the
# location for the virtualenv is a bad idea since we won't be able to
# activate it. The check for defined variables is from
# http://stackoverflow.com/questions/228544/how-to-tell-if-a-string-is-not-defined-in-a-bash-shell-script
if [[ ${LR_ENV_NAME_IS_DIR} -gt 0 ]] && \
    [[ ! -z "${WORKON_HOME+defined}" ]] && \
    [[ ! -z "${PIP_VIRTUALENV_BASE+defined}" ]] && \
    [[ "${WORKON_HOME}" == "${PIP_VIRTUALENV_BASE}" ]] ; then
    echo "You've specified a directory path for the virtualenv with virtualenvwrapper configured."
    echo "virtualenvwrapper won't work. Please specify a name without any \"/\" characters." >&2
    exit 1
# Take into account if pip is configured to install to a location
# other than virtualenvwrapper's WORKON_HOME. See Using pip with
# virtualenvwrapper at http://pypi.python.org/pypi/pip for further details.
elif  [[ ! -z  "${PIP_VIRTUALENV_BASE+defined}" ]] ; then
    PIP_ENV="${LR_ENV_NAME}"
    LR_ENV_NAME="${PIP_VIRTUALENV_BASE}/${LR_ENV_NAME}"
# Otherwise create a virtualenv in the user's home.
else
    LR_ENV_NAME="$HOME/${LR_ENV_NAME}"
    PIP_ENV="${LR_ENV_NAME}"
fi

# Check to see if we can write to the directory where the virtualenv
# will be created.
if [[ ! -w $(dirname "${LR_ENV_NAME}") ]] ; then
    echo "Can't write to" $(dirname "${LR_ENV_NAME}")
    echo "Please specify a location to which ${USER} can write. Aborting."
    exit 1
fi

# Check to see if we already have something at the specified location
# and exit if so. We don't want to overwrite stuff.
if [[ -d "${LR_ENV_NAME}" ]] ; then
    echo "A directory already exists at: ${LR_ENV_NAME}"
    echo "Please specify a different location."
    exit 1
fi

# create the virtualenv and install the python dependencies
echo "Creating a virtualenv at ${LR_ENV_NAME}."
virtualenv --no-site-packages --distribute ${LR_ENV_NAME}
echo "Installing LR and its dependencies into ${LR_ENV_NAME} virtualenv as an editable package."
pip --environment="${LR_ENV_NAME}" install -e ../LR

# clean up if we downloaded distribute
for i in distribute*tar.gz ; do
    echo "Removing ${i} after installation."
    rm -f "${i}"
done

if [[ "${OSTYPE}" == "darwin10.0" ]] ;  then
    get_xcode_version
    if [[ ${XCODE_VER%%.*} -gt 3 ]] ; then
        echo "========================================================================"
        echo "Xcode 4 detected won't install lxml. Tests won't work without lxml."
        echo "See https://gist.github.com/963298 or"
        echo "https://bugs.launchpad.net/lxml/+bug/738500 for instructions on building lxml."
        echo "========================================================================"
    else
        echo "Installing lxml."
        pip --environment="${LR_ENV_NAME}" install lxml
    fi
else
    echo "Installing lxml."
    pip --environment="${LR_ENV_NAME}" install lxml
fi

# Show the user what to do next.
echo
echo "Installed the LR python packages."
echo "You may now activate the newly created virtualenv with the following command:"

if [[ ! -z "${WORKON_HOME+defined}" ]] ; then
    echo "workon ${PIP_ENV}"
else
    echo "cd ${LR_ENV_NAME} && source bin/activate"
fi

echo "========================================================================"
echo "All the software installation is done."
echo "Next steps:"
echo "Set up a config file in the LR directory."
echo "You may copy ../LR/development.ini.orig to ../LR/development.ini"
echo "Then set up the node by running the ../config/setup_node.py script."
echo
echo "Enjoy working with the Learning Registry."
