# Title       : teampass.py
# Date        : Sat Jun  9 21:09:45 CEST 2018
# Author      : Jose Andres Arias Velichko <a.arias@.paislinux.es>
# Version     : See bellow "_version_" line
# Copyright   : 2018 Jose Andres Arias Velichko
# License     : GNU GPL-2.0
# Description : Python libraries to work with Teampass API
#
#  * This software is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
_version_ = '0.10.dev10'

import requests
import re
import pprint
import json
import sys

# My Error Class
class BadTeampassResponse(Exception):
    '''Returned on teampass connection errors'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
class MalformedTeampassData(Exception):
    '''Returned on badly formated data'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


# Main Teampass class
class teampass:
    def __init__(self, url, key):
        self.base_url = url
        self.api_key = key
        self.__json_response = []

    # Class Functions

    def get_folders(self, folders):
        "Read TP URL and return list of folders from TP."
        url = self.base_url + '/api/index.php/read/folder/' + folders +  '?apikey=' + self.api_key
        myResponse = requests.get(url,verify=True)
        # Check the result
        if(myResponse.ok):
            self.__json_response = myResponse.json()
            return self.hosts_json2dict()
        else:
            raise BadTeampassResponse('Teampass server returned en error')

    def __parse_description(self, description):
        "Parses description string and returns dict with config from it"
        data_locator = '---Auto Managed Data: Do NOT edit bellow this line---'
        data_location = description.find(data_locator)
        #sys.stderr.write('Found Managed data at {}\n'.format(data_location))

        if data_location >= 0:
            try:
                data = description[(data_location + len(data_locator)):].replace('&quot;','"').replace('&nbsp;',' ').replace('<br />','\n')
                #sys.stderr.write('Data: {}\n'.format(data))
                return json.loads(data)
            except ValueError as details:
                raise MalformedTeampassData(details)
        else:
            return None


    def hosts_json2dict(self):
        "Converts json data to confortable to use dict"
        hosts_dict = {}

        for host_data in self.__json_response:
            label = re.split('[:@]',host_data["label"])
            url = host_data["url"].replace('/','').split(':')
            # Check if this is a valid type of entry
            if ( (label[0] != 'os') or (url[0] != 'ssh') ):
                print ("\tNot a valid host type, ignoring...")
                next
            # If port has been set in the URL, use it, else use the default 22
            if ( len(url) < 3 ):
                port = 22
            else:
                port = int(url[2])
            # Fill dictionary with data
            hosts_dict[label[2],label[1]] = {"pw": host_data["pw"],
                    "port": port, "id": host_data["id"]}
            try:
                additional_data = self.__parse_description(host_data["description"])
            except MalformedTeampassData:
                additional_data = None

            if additional_data is not None:
                hosts_dict[label[2],label[1]].update(additional_data)

        return hosts_dict

    def get_new_pw(self, password_rules = '12;1;1;1;1'):
        '''Generate new password using TP'''
        url = self.base_url + '/api/index.php/new_password/' + password_rules + '0;0?apikey=' + self.api_key
        myResponse = requests.get(url,verify=True)
        # Check the result
        if(myResponse.ok):
            self.__json_response = myResponse.json()
            return self.__json_response["password"]
        else:
            raise BadTeampassResponse('Teampass server returned en error')


