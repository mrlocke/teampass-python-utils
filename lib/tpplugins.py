# Title       : tpplugins.py
# Date        : Mon Jun 11 18:24:47 CEST 2018
# Author      : Jose Andres Arias Velichko <a.arias@.paislinux.es>
# Version     : See bellow "_version_" line
# Copyright   : 2018 Jose Andres Arias Velichko
# License     : GNU GPL-2.0
# Description : Teampass-changer plugins dependencies and it's principal
#               functions
#
#  * This software is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
_version_ = '0.10.dev10'


# Load the plugin provider module as required
import pssh


''' map the plugin type to an init function(s) of your module
    it will be called with:
        main_host_data = dictionary of {
            "host":     hostname,
            "user":     username,
            "id":       teampass object ID,
            "pw":       password from teampass
            "newpw":    New password to set
            ... -> Other data obtained from json formatted hashed array included
                   in the description field of the record bellow the line
                "---Auto Managed Data: Do NOT edit bellow this line---"

                Example json format:
                >>>>---Auto Managed Data: Do NOT edit bellow this line---
                >>>>{
                >>>> "PasswordType": "OS",
                >>>> "OS": "Linux",
                >>>> "Plugin": "ssh_sudo",
                >>>> "Plugin_args": "sudo passwd"
                >>>> "Additional_account": "sudo_user"
                >>>>}
                "Plugin":               Will be used to call the corresponding plugin
                "Additional_account":   Used for additional_host_data (see bellow)
        additional_host_data = If "Additional_account" was present in the json, it will also submit a dict with data of this additional account for this server

    The function must return True on success, and False on failure.

'''
plugins = { "ssh": pssh.ssh_plugin,
        "ssh_sudo": pssh.ssh_sudo_plugin
        }
