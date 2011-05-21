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

# The default name for the virtualenv.
LR_ENV_NAME="lr"

echo
echo "========================================================================"
echo "This script will install the python packages to a virtualenv."
echo "It requires:"
echo "C/C++ compilers"
echo "Python including header files"
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

# Set the name of the virtualenv if one is specified. We do no
# sanitization of the passed value. Fragile stuff here.
if [[ $# -gt 0 ]] ; then
    LR_ENV_NAME="${1}"
fi

PIP_ENV="${LR_ENV_NAME}"

# check if LR_ENV_NAME contains a directory separator
LR_ENV_NAME_IS_DIR=$(awk -v env_name="${LR_ENV_NAME}" -v path_sep="/" \
    'BEGIN { print index(env_name, path_sep) }')

check_if_present CC_PATH "c/c++ compiler"
check_if_present PYTHON_PATH "python" # how do we check for header files?
check_if_present VIRTUALENV_PATH "virtualenv"

echo "Found python at: ${PYTHON_PATH}"
echo "Found virtualenv at: ${VIRTUALENV_PATH}"
echo "Found c compiler at: ${CC_PATH}"

# If virtualenvwrapper is set up, passing a directory path as the
# location for the virtualenv is a bad idea since we won't be able to
# activate it.
if [[ ${LR_ENV_NAME_IS_DIR} -gt 0 ]] && \
    [[ "${WORKON_HOME}" == "${PIP_VIRTUALENV_BASE}" ]] ; then
    echo "You've specified a directory path for the virtualenv with virtualenvwrapper configured."
    echo "virtualenvwrapper won't work. Please specify a name without any \"/\" characters." >&2
    exit 1
# Take into account if pip is configured to install to a location
# other than virtualenvwrapper's WORKON_HOME. See Using pip with
# virtualenvwrapper at http://pypi.python.org/pypi/pip for further details.
elif  [[ ${PIP_VIRTUALENV_BASE} ]] ; then
    LR_ENV_NAME="${PIP_VIRTUALENV_BASE}/${LR_ENV_NAME}"
    PIP_ENV=$(basename "${LR_ENV_NAME}")
# Otherwise create a virtualenv in the user's home.
else
    LR_ENV_NAME="$HOME/${LR_ENV_NAME}"
    PIP_ENV="${LR_ENV_NAME}"
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
pip --environment=${LR_ENV_NAME} install -e ../LR

# clean up if we downloaded distribute
for i in distribute*tar.gz ; do
    echo "Removing ${i} after installation."
    rm -f "${i}"
done

# Show the user what to do next.
echo
echo "Installed the LR python packages."
echo "You may now activate the newly created virtualenv with the following command:"

if [[ ${WORKON_HOME} ]] ; then
    echo "workon ${LR_ENV_NAME}"
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
