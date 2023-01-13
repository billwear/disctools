#!/usr/bin/python3

"""
discourse: object library for accessing the discourse API
"""

from pathlib import Path
import errno, os, requests, glob, sys
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import requests
# import json, sys, subprocess, datetime

repo_path = ""

class Discourse_Doc:

    ## how do we construct a new discourse doc?
    def __init__(self,site):

        ### debug/test flag
        self.debug = 0

        ### capture credentials
        self.base_url = site.credentials["base_url"]
        self.username = site.credentials["api_username"]
        self.api_key = site.credentials["api_key"]
        self.repo_path = site.credentials["repo_path"]

        ### set up file list
        file_list = []
        
        ### what document would you like to edit?
        print("Enter \"new\" if this you already know this is a new document")
        self.title = input("Approximate document title? : ")

        if self.debug == 1:
            print("debug: requested title is",self.title)

        if self.title == "new":
            self.new_document()
        else:
            #### find closest matching document titles in git repository
            ##### convert entered title to all lower case
            doc_title = self.title.lower()

            ##### convert all spaces in title to "-"
            doc_title = doc_title.replace(" ","-")
            
            i = 0
            for file in glob.glob(self.repo_path + '/src/*' + doc_title + '*.md'):
                file_list.append(file)
                temp = file
                print(i,"=",file.split('/')[-1])
                i += 1
            print(i,"= none of these, just exit")

            choice = int(input("choose file by #? : "))
            if choice >= i:
                print("exiting")
                sys.exit(0)
            else:
                self.md_master = load_markdown_master(file_list[choice])
                self.dc_master = load_discourse_doc()
                self.diff_file = diff_discourse_and_markdown()

    def load_markdown_master(self,file_path):
        file = open(file_path,mode='r')
        markdown_string = file.read()
        file.close()
        return markdown_string
        
    def load_discourse_doc(self):

    def diff_discourse_and_markdown():
        
    def new_document(self):
        if self.debug == 1:
            print("user requested new document")
            
# how do we model a discourse site?
class Discourse_Site:

    ## how do we construct a new discourse site?
    def __init__(self):
        
        ## debug/test flag
        self.debug = 0

        ### what is the URL of the discourse site?
        print("Enter \"default\" if you have a default dc.yaml file")
        self.url = input("What is the URL of the discourse site? : ")
        if self.debug:
            print("User entered URL",self.url)
            
        ### do we have a local config file listing that site?
        error_code = self.get_credentials(self.url)
        
        #### if so, set the parameters from the config file
        if error_code == 0:
            if self.debug:
                print("debug: pulled credentials as follows")
                print("debug: ",self.credentials)
            self.url = self.credentials["base_url"]
            self.username = self.credentials["api_username"]
            self.api_key = self.credentials["api_key"]
            self.repo_path = self.credentials["repo_path"]
                
        #### if not, query the user for discourse details
        if error_code != 0:
            if self.debug:
                print(os.strerror(error_code))
            print("No matching configuration found")
            self.username = input("API username? :")
            self.api_key = input("API key value? :")
            self.repo_path = input("FQ path to local git repository? :")

        ### attempt a simple query to confirm access to the discourse server
        try:
            r = requests.get(self.url, auth=(self.username, self.api_key))
            if r.status_code == 200:
                print("successfully connected to",self.url)
            else:
                print("could not access",self.url,"with the credentials given")
                print("error was",r.status_code)
        except:
            print("could not access",self.url,"with the credentials given")

        repo_path = self.credentials["repo_path"]
   #     discourse_doc = Discourse_Doc(self.credentials)
        
    def get_credentials(self,url):
        
        if self.debug:
            print("attempting to get credentials from default location")

        def_cred_loc = str(Path.home()) + "/.config/dc.yaml"

        try:
            cfile = open(def_cred_loc, "r")
        except:
            return errno.ENOENT
        
        credentials = load(cfile, Loader=Loader)
        cfile.close()

        if self.url == "default" or credentials["base_url"] == self.url:
            self.credentials = credentials
            return 0
        else:
            return errno.ENXIO
        

#  - md_get_last_edit_timestamp(revision_json):
#    -- accepts: latest revision JSON for first post of a given topic
#       (note that in the MAAS doc world, the first post is the actual documentation)
#    -- returns: the discourse timestamp of the last edit, as a string (in Zulu time)
#  - md_get_last_editor_username(revision_json):
#    -- accepts: latest revision JSON for first post of a given topic
#       (note that in the MAAS doc world, the first post is the actual documentation)
#    -- returns: the username of the user who last edited the first post, as a string
#  - md_api_get_topic(topic_id, credentials):
#    -- accepts: a discourse topic ID (integer), and a set of API credentials (dictionary)
#    -- returns: the full JSON representation of the topic
#  - md_api_get_latest_revision(topic_id, credentials):
#    -- accepts: a discourse topic ID (integer), and a set of API credentials (dictionary)
#    -- returns: the latest revision JSON for the first post of the given topic
#  - md_api_get_post(post_id, credentials):
#    -- accepts: a discourse post ID (integer), and a set of API credentials (dictionary)
#    -- returns: the full JSON representation of the post
#  - md_api_put_post(post_id, markdown, credentials):
#    -- accepts: a discourse post ID (integer), a buffer containing the markdown to push, and a set of API credentials (dictionary)
#    -- returns: the JSON that was actually written to post post_id
#  - md_api_new_topic(title, markdown, credentials):
#    -- accepts: a topic title (string), a buffer containing the markdown to push,
#       and a set of API credentials (dictionary)
#    -- returns: the topic number of the newly-created topic
#  - md_api_has_been_updated(topic_id, interval, credentials):
#    -- accepts: a discourse topic ID (integer), an interval in hours (integer),
#       and a set of API credentials (dictionary)
#    -- returns: a boolean indicating whether topic_id has been updated in the last
#       interval hours
#  - md_get_credentials(credential_file_path):
#    -- accepts: a file path to a valid MAAS docs API credential set, which includes
#       a username, an API key, and a valid MAAS docs API URL
#    -- returns: a dictionary containing the API credentials
#  - md_get_post_number(topic_json):
#    -- accepts: the full JSON representation of a topic
#    -- returns: an integer corresponding to the post number
#  - md_get_markdown_content(post_json):
#    -- accepts: the full JSON representation of a post
#    -- returns: a string containing the markdown content of the post (essentially, the markdown corresponding to the discourse doc page content)
#  - md_is_later_than(timestamp_1, timestamp_2):
#    -- accepts: two timestamps, as discourse timestamp strings
#    -- returns: a boolean indicating whether timestamp1 is later than timestamp2
#  - md_is_earlier_than(timestamp_1, timestamp_2):
#    -- accepts: two timestamps, as discourse timestamp strings
#    -- returns: a boolean indicating whether timestamp1 is earlier than timestamp2
#  - md_is_identical_to(timestamp_1, timestamp_2):
#    -- accepts: two timestamps, as discourse timestamp strings
#    -- returns: a boolean indicating whether timestamp1 is identical to timestamp2
# """

# import json, sys, subprocess, errno, datetime, os
# from datetime import timedelta
# from yaml import load, dump
# try:
#     from yaml import CLoader as Loader, CDumper as Dumper
# except ImportError:
#     from yaml import Loader, Dumper

# def md_get_last_edit_timestamp(revision_json):
#     '''
#     pulls the last edited timestamp from the passed JSON dictionary containing
#     information about the latest revision of a topic.
#     '''

#     # copy last_edit_timestamp to local variable
#     created_at = revision_json["created_at"]

#     # return error code, last_edit_timestamp to caller
#     return(0, created_at)

# def md_get_last_editor_username(revision_json):
#     '''
#     pulls the username of the user who last edited a topic from the passed JSON
#     dictionary containing information about the latest revision of a topic.
#     '''
#     # copy last_editor_username to local variable
#     username = revision_json["username"]

#     # return error code, last_editor_username to caller
#     return(0, username)

# def md_api_get_topic(topic_id, credentials):
#     '''
#     gets topic_id from the Discourse server indicated in the credentials;
#     handles Discourse API wait requests and other transient errors,
#     in case a large number of calls are made in a short time period
#     '''

#     # set rate limit error flag to True
#     rate_limit_error = True

#     # while rate limit error is True
#     while rate_limit_error == True:

#         ## do the curl call
#         proc = subprocess.Popen(
#             [
#                 "curl",
#                 "-s",
#                 "-X",
#                 "GET",
#                 "-H",
#                 "Api-Key: " + credentials["api_key"],
#                 "-H",
#                 "Api-Username: " + credentials["api_username"],
#                 "-H",
#                 "Content-Type: application/json",
#                 credentials["base_url"] + "/t/{" + str(topic_id) + "}.json",
#             ],
#             stdout=subprocess.PIPE,
#         )

#         ## read the curl result into a usable buffer
#         output = proc.stdout.read()

#         ## try to convert the result to json
#         try:
#             topic_json = json.loads(output)
#         except:
#             ### handle "topic doesn't exist" error
#             print("error in md_api_get_topic", errno.ENODATA, ": Topic doesn't exist")
#             print(output)
#             sys.exit(errno.ENODATA)

#         ## try to see if there's a rate_limit error
#         try:
#             ### if so, sleep for 20s and continue the loop
#             if topic_json["error_type"] == "rate_limit":
#                 rate_limit_error = True
#                 time.sleep(20)
#                 continue;
#         except:
#             return(topic_json)


# def md_api_get_latest_revision(topic_id, credentials):
#     '''
#     gets latest revision for topic_id from the Discourse server indicated in
#     the credentials; handles Discourse API wait requests and other transient
#     errors, in case a large number of calls are made in a short time period.
#     '''

#     # get the topic to get the post_id from it
#     try:
#         error, topic_json = md_api_get_topic(topic_id, credentials)
#     except error != 0:
#         print("error", errno.ENODATA, ": couldn't pull topic JSON for latest revision")
#         sys.exit(errno.ENODATA)

#     # get the post_id from the passed topic_id
#     try:
#        error, post_id = md_get_post_number(topic_json)
#     except:
#         print("error", errno.ENODATA, ": couldn't get post number for latest revision")

#     # set rate limit error flag to True
#     rate_limit_error = True

#     # while rate limit error is True
#     while rate_limit_error == True:

#         ## do the curl call
#         proc = subprocess.Popen(
#             [
#                 "curl",
#                 "-s",
#                 "-X",
#                 "GET",
#                 "-H",
#                 "Api-Key: " + credentials["api_key"],
#                 "-H",
#                 "Api-Username: " + credentials["api_username"],
#                 "-H",
#                 "Content-Type: application/json",
#                 credentials["base_url"] + "/posts/" + str(post_id) + "/revisions/latest.json",
#             ],
#             stdout=subprocess.PIPE,
#         )


#         ## read the curl result into a usable buffer
#         output = proc.stdout.read()

#         # convert the result to json
#         try:
#             latest_revision_json = json.loads(output)
#         ### handle "topic doesn't exist" error
#         except:
#             print("error", errno.ENOEXIST, ": couldn't pull latest revision")

#         ## try to see if there's a rate_limit error
#         try:
#             ### if so, sleep for 20s and continue the loop
#             if post_json["error_type"] == "rate_limit":
#                 rate_limit_error = True
#                 time.sleep(20)
#                 continue
#         ## if no rate error
#         except:
#             ### return a "no-error" code and the revision json
#             return(latest_revision_json)

# def md_api_get_post(post_id, credentials):
#     '''
#     gets post_id from the Discourse server indicated in the credentials;
#     handles Discourse API wait requests and other transient errors, in case a
#     large number of calls are made in a short time period.
#     '''
#     # set rate limit error flag to True
#     rate_limit_error = True

#     # while rate limit error is True
#     while rate_limit_error == True:

#         ## do the curl call
#         proc = subprocess.Popen(
#             [
#                 "curl",
#                 "-s",
#                 "-X",
#                 "GET",
#                 "-H",
#                 "Api-Key: " + credentials["api_key"],
#                 "-H",
#                 "Api-Username: " + credentials["api_username"],
#                 "-H",
#                 "Content-Type: application/json",
#                 credentials["base_url"] + "/posts/{" + str(post_id) + "}.json",
#             ],
#             stdout=subprocess.PIPE,
#         )


#         ## read the curl result into a usable buffer
#         output = proc.stdout.read()

#         ## try to convert the result to json
#         try:
#             post_json = json.loads(output)
#         ### handle "topic doesn't exist" error
#         except:
#             print("error", errno.ENODATA, ": couldn't get post JSON for post ID", post_id)
#             sys.exit(errno.ENODATA)

#         ## try to see if there's a rate_limit error
#         try:
#             ### if so, sleep for 20s and continue the loop
#             if post_json["error_type"] == "rate_limit":
#                 rate_limit_error = True
#                 time.sleep(20)
#                 continue;
#         ## if no rate error
#         except:
#             ### return a "no-error" code and the revision json
#             return(post_json)

# def md_api_change_title(post_id, put_buffer, new_title, credentials):
#     '''
#     change the title of topic_id on the Discourse server indicated in the credentials;
#     handles Discourse API wait requests and other transient errors, in case a large
#     number of calls are made in a short time period.
#     '''
#     # pad the markdown to 9000 characters to avoid a discourse bug
#     put_buffer = put_buffer.ljust(9000)

#     # create a dictionary buffer for the new title
#     data = {}

#     # load the new_title in the appropriate json key
#     data["title"] = new_title
#     data["raw"] = put_buffer

#     # open a temp file to store the markdown ad json
#     # (the put works better if it draws from a file)
#     f = open("foo.json", "w")

#     # convert the data dictionary to json and store it in the temp file
#     f.write(json.dumps(data))

#     # close the temp file
#     f.close()

#     # copy the auth data into individual parameters
#     apikey = "Api-Key: " + credentials["api_key"]
#     apiusername = "Api-Username: " + credentials["api_username"]

#     # build the appropriate URL based on the calling sequence
#     url = credentials["base_url"] + "/posts/{" + str(post_id) + "}.json"

#     # set rate_limit_error flag
#     rate_limit_error = True

#     # while rate limit error is True
#     while rate_limit_error == True:

#         ## use the curl command to post the new_title to the post on discourse,
#         ## and read the result into a usable return buffer
#         proc= subprocess.Popen(
#             [
#                 "curl",
#                 "-s",
#                 "-X",
#                 "PUT",
#                 url,
#                 "-H",
#                 apikey,
#                 "-H",
#                 apiusername,
#                 "-H",
#                 "Content-Type: application/json",
#                 "-d",
#                 "@foo.json",
#             ],
#             stdout=subprocess.PIPE,
#         )

#         ## read the curl result into a usable buffer
#         output = proc.stdout.read()

#         ## try to convert the result to json
#         try:
#             post_json = json.loads(output)
#         ### handle "topic doesn't exist" error
#         except:
#             print("error", errno.ENODATA, ": post ", post_id, "doesn't exist when trying to change title")
#             sys.exit(errno.ENODATA)

#         ## try to see if there's a rate_limit error
#         try:
#             ### if so, sleep for 20s and continue the loop
#             if post_json["error_type"] == "rate_limit":
#                 rate_limit_error = True
#                 time.sleep(20)
#                 continue;
#         ## if no rate error
#         except:
#             ### remove the temporary json file
#             os.remove("foo.json")
#             ### return a clear error and the post_json
#             return(post_json)

# def md_api_delete_topic(topic_number, credentials):
#     '''
#     deletes a discourse topic with the passed topic number.  accepts: a topic number (integer) and a set of API credentials (dictionary); returns nothing. 
#     '''

#     # copy the auth data into individual parameters
#     apikey = "Api-Key: " + credentials["api_key"]
#     apiusername = "Api-Username: " + credentials["api_username"]

#     # build the appropriate URL based on the calling sequence
#     url = credentials["base_url"] + "/t/{" + topic_number + "}.json"

#     ## use the curl command to post put_buffer to the post on discourse,
#     ## and read the result into a usable return buffer
#     proc= subprocess.Popen(
#         [
#             "curl",
#             "-s",
#             "-X",
#             "DELETE",
#             url,
#             "-H",
#             apikey,
#             "-H",
#             apiusername,
#         ],
#         stdout=subprocess.PIPE,
#     )

# def md_api_new_topic(title, markdown, category, credentials):
#     '''
#     creates a new discourse topic with the passed title, and posts the passed markdown to the new topic; accepts: a topic title (string), a buffer containing the markdown to push, a category for the topic, and a set of API credentials (dictionary); returns: the topic number of the newly-created topic.
#     '''

#     # pad the markdown to 9000 characters to avoid a discourse bug
#     # pad the markdown to 9000 characters to avoid a discourse bug
#     put_buffer = markdown.ljust(9000)

#     # create a dictionary buffer for the put_buffer
#     data = {}

#     # load the put_buffer in the appropriate json key
#     data["title"] = title
#     data["raw"] = put_buffer
#     data["category"] = category

#     # open a temp file to store the markdown ad json
#     # (the put works better if it draws from a file)
#     f = open("foo.json", "w")

#     # convert the data dictionary to json and store it in the temp file
#     f.write(json.dumps(data))

#     # close the temp file
#     f.close()

#     # copy the auth data into individual parameters
#     apikey = "Api-Key: " + credentials["api_key"]
#     apiusername = "Api-Username: " + credentials["api_username"]

#     # build the appropriate URL based on the calling sequence
#     url = credentials["base_url"] + "/posts.json"

#     # set rate_limit_error flag
#     rate_limit_error = True

#     # while rate limit error is True
#     while rate_limit_error == True:

#         ## use the curl command to post put_buffer to the post on discourse,
#         ## and read the result into a usable return buffer
#         proc= subprocess.Popen(
#             [
#                 "curl",
#                 "-s",
#                 "-X",
#                 "POST",
#                 url,
#                 "-H",
#                 apikey,
#                 "-H",
#                 apiusername,
#                 "-H",
#                 "Content-Type: application/json",
#                 "-d",
#                 "@foo.json",
#             ],
#             stdout=subprocess.PIPE,
#         )

#         ## read the curl result into a usable buffer
#         output = proc.stdout.read()

#         ## try to convert the result to json
#         try:
#             post_json = json.loads(output)
#         ### handle "topic doesn't exist" error
#         except:
#             print("error", errno.ENODATA, ": topic not created")
#             sys.exit(errno.ENODATA)

#         ## try to see if there's a rate_limit error
#         try:
#             ### if so, sleep for 20s and continue the loop
#             if post_json["error_type"] == "rate_limit":
#                 rate_limit_error = True
#                 time.sleep(20)
#                 continue;
#         ## if no rate error
#         except:
#             ### remove the temporary json file
#             os.remove("foo.json")
#             ### return a clear error and the post_json
#             return(post_json["topic_id"])
    
# def md_api_put_post(post_id, markdown, credentials):
#     '''
#     puts a new version of topic_id the Discourse server indicated in the credentials;
#     handles Discourse API wait requests and other transient errors, in case a large
#     number of calls are made in a short time period.
#     '''

#     debug = False
    
#     if debug == True:
#         print("md_api_put_post::entering, post id", post_id)
    
#     # pad the markdown to 9000 characters to avoid a discourse bug
#     put_buffer = markdown.ljust(9000)
#     if debug == True:
#         print("md_api_put_post::just padded put_buffer for post id", post_id)

#     # create a dictionary buffer for the put_buffer
#     data = {}
#     if debug == True:
#         print("md_api_put_post::just created dict buffer for post id", post_id)

#     # load the put_buffer in the appropriate json key
#     data["raw"] = put_buffer
#     if debug == True:
#         print("md_api_put_post::just loaded put_buffer for post id", post_id)

#     # open a temp file to store the markdown ad json
#     # (the put works better if it draws from a file)
#     f = open("foo.json", "w")
#     if debug == True:
#         print("md_api_put_post::opened foo.json for post id", post_id)

#     # convert the data dictionary to json and store it in the temp file
#     f.write(json.dumps(data))
#     if debug == True:
#         print("md_api_put_post::wrote to foo.json for post id", post_id)

#     # close the temp file
#     f.close()
#     if debug == True:
#         print("md_api_put_post::closed foo.json for post id", post_id)

#     # copy the auth data into individual parameters
#     apikey = "Api-Key: " + credentials["api_key"]
#     apiusername = "Api-Username: " + credentials["api_username"]
#     if debug == True:
#         print("md_api_put_post::copied creds for post id", post_id)

#     # build the appropriate URL based on the calling sequence
#     url = credentials["base_url"] + "/posts/{" + str(post_id) + "}.json"
#     if debug == True:
#         print("md_api_put_post::formulated URL for post id", post_id)

#     # set rate_limit_error flag
#     rate_limit_error = True
#     if debug == True:
#         print("md_api_put_post::just init'd rate_limit_error for post_id", post_id)

#     # while rate limit error is True
#     while rate_limit_error == True:
#         if debug == True:
#             print("md_api_put_post::top of while rate_limit_error loop")

#         ## use the curl command to post put_buffer to the post on discourse,
#         ## and read the result into a usable return buffer
#         proc= subprocess.Popen(
#             [
#                 "curl",
#                 "-s",
#                 "-X",
#                 "PUT",
#                 url,
#                 "-H",
#                 apikey,
#                 "-H",
#                 apiusername,
#                 "-H",
#                 "Content-Type: application/json",
#                 "-d",
#                 "@foo.json",
#             ],
#             stdout=subprocess.PIPE,
#         )
#         if debug == True:
#             print("md_api_put_post::right after curl for post id", post_id)

#         ## read the curl result into a usable buffer
#         output = proc.stdout.read()
#         if debug == True:
#             print("md_api_put_post::after proc.stdout.read()")

#         ## try to convert the result to json
#         try:
#             if debug == True:
#                 print("md_api_put_post::trying to convert post_json to json")
#             post_json = json.loads(output)

#         ### handle "topic doesn't exist" error
#         except:
#             if debug == True:
#                 print("error", errno.ENODATA, ": post", post_id, "doesn't exist")
#             sys.exit(errno.ENODATA)

#         ## try to see if there's a rate_limit error
#         try:
#             if debug == True:
#                 print("md_api_put_post :: trying rate_limit_error")

#             ### if so, sleep for 20s and continue the loop
#             if post_json["error_type"] == "rate_limit":
#                 rate_limit_error = True
#                 if debug == True:
#                     print("md_api_put_post::rate_limit_error")
#                 time.sleep(20)
#                 continue;
#         ## if no rate error
#         except:
#             ### remove the temporary json file
#             os.remove("foo.json")
#             ### return a clear error and the post_json
#             return(post_json)

# def md_api_has_been_updated(topic_id, interval, credentials):
#     '''
#     checks to see whether a topic has been updated in the last interval hours
#     '''

#     # get the last revision for the specified topic
#     error, last_revision_json = md_api_get_latest_revision( topic_id, credentials )

#     # extract the timestamp from the last revision information
#     error, last_rev_timestamp = md_get_last_edit_timestamp(last_revision_json)

#     # fix the timestamp so it can be compared with current system time
#     last_rev_timestamp = last_rev_timestamp.replace("T"," ")
#     last_rev_timestamp = last_rev_timestamp.replace("Z"," ")

#     # get the current timestamp, consistent with the Discourse server
#     ts = datetime.datetime.utcnow()

#     # subtract "interval" from the current timestamp
#     new_time = ts - timedelta(hours=interval)

#     # compare the subtracted timestamp to the last revision timesstamp
#     if str(new_time) < last_rev_timestamp:
#         return True
#     else:
#         return False


# def md_get_post_number(topic_json):
#     '''
#     pulls the post number for the first post in a topic (needed for most topic
#     modifications) from the passed JSON dictionary containing information about
#     a topic.
#     '''

#     # copy post_number to local variable
#     try:
#         post_id = topic_json["post_stream"]["posts"][0]["id"]
#     except:
#         print("error", errno.ENODATA, ": post number", post_id, "doesn't exist")
#         sys.exit(errno.ENODATA)

#     # return post_nubmer to caller
#     return(post_id)

# def md_get_markdown_content(post_json):
#     '''
#     pulls the actual topic markdown content from the passed JSON dictionary
#     containing information about a post.
#     '''
#     # copy raw component to local variable
#     try:
#         markdown = post_json["raw"]
#     except:
#         print("error", errno.ENODATA, ": markdown content doesn't exist")
#         sys.exit(errno.ENODATA)

#     # return error code, markdown_content to caller
#     return(markdown)

# def md_is_later_than(timestamp_1, timestamp_2):
#     '''
#     compares two Discourse timestamps as strings and returns True if the first
#     passed timestamp is later than the second.  Discourse timestamps in JSON payloads
#     are formatted as strings in a way that does not require converting them to
#     datetime types to compare them.
#     '''

#     # return_value = ts1 > ts2
#     return(timestamp_1 > timestamp_2)

# def md_is_earlier_than(timestamp_1, timestamp_2):
#     '''
#     compares two Discourse timestamps as strings and returns True if the first
#     passed timestamp is earlier than the second.
#     '''

#     # return_value = ts1 < ts2
#     return(timestamp_1 < timestamp_2)

# def md_is_identical_to(timestamp_1, timestamp_2):
#     '''
#     compares to Discourse timestamps as strings and returns True if they
#     are identical.
#     '''

#     # return_value = ts1 ==n ts2
#     return(timestamp_1 == timestamp_2)
