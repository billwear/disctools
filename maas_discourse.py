#!/usr/bin/python3

"""
maas_discourse: convenience functions for accessing the MAAS docs API; note that the functions
containing "_api_" in their name access the API, those without work on passed data instead.

 - md_get_last_edit_timestamp(revision_json):
   -- accepts: latest revision JSON for first post of a given topic
      (note that in the MAAS doc world, the first post is the actual documentation)
   -- returns: the discourse timestamp of the last edit, as a string (in Zulu time)
 - md_get_last_editor_username(revision_json):
   -- accepts: latest revision JSON for first post of a given topic
      (note that in the MAAS doc world, the first post is the actual documentation)
   -- returns: the username of the user who last edited the first post, as a string
 - md_api_get_topic(topic_id, credentials):
   -- accepts: a discourse topic ID (integer), and a set of API credentials (dictionary)
   -- returns: the full JSON representation of the topic
 - md_api_get_latest_revision(topic_id, credentials):
   -- accepts: a discourse topic ID (integer), and a set of API credentials (dictionary)
   -- returns: the latest revision JSON for the first post of the given topic
 - md_api_get_post(post_id, credentials):
   -- accepts: a discourse post ID (integer), and a set of API credentials (dictionary)
   -- returns: the full JSON representation of the post
 - md_api_put_post(post_id, markdown, credentials):
   -- accepts: a discourse post ID (integer), a buffer containing the markdown to push, and a set of API credentials (dictionary)
   -- returns: the JSON that was actually written to post post_id
 - md_api_new_topic(title, markdown, credentials):
   -- accepts: a topic title (string), a buffer containing the markdown to push,
      and a set of API credentials (dictionary)
   -- returns: the topic number of the newly-created topic
 - md_api_has_been_updated(topic_id, interval, credentials):
   -- accepts: a discourse topic ID (integer), an interval in hours (integer),
      and a set of API credentials (dictionary)
   -- returns: a boolean indicating whether topic_id has been updated in the last
      interval hours
 - md_get_credentials(credential_file_path):
   -- accepts: a file path to a valid MAAS docs API credential set, which includes
      a username, an API key, and a valid MAAS docs API URL
   -- returns: a dictionary containing the API credentials
 - md_get_post_number(topic_json):
   -- accepts: the full JSON representation of a topic
   -- returns: an integer corresponding to the post number
 - md_get_markdown_content(post_json):
   -- accepts: the full JSON representation of a post
   -- returns: a string containing the markdown content of the post (essentially, the markdown corresponding to the discourse doc page content)
 - md_is_later_than(timestamp_1, timestamp_2):
   -- accepts: two timestamps, as discourse timestamp strings
   -- returns: a boolean indicating whether timestamp1 is later than timestamp2
 - md_is_earlier_than(timestamp_1, timestamp_2):
   -- accepts: two timestamps, as discourse timestamp strings
   -- returns: a boolean indicating whether timestamp1 is earlier than timestamp2
 - md_is_identical_to(timestamp_1, timestamp_2):
   -- accepts: two timestamps, as discourse timestamp strings
   -- returns: a boolean indicating whether timestamp1 is identical to timestamp2
"""

import json, sys, subprocess, errno, datetime, os
from datetime import timedelta
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def md_get_last_edit_timestamp(revision_json):
    '''
    pulls the last edited timestamp from the passed JSON dictionary containing
    information about the latest revision of a topic.
    '''

    # copy last_edit_timestamp to local variable
    created_at = revision_json["created_at"]

    # return error code, last_edit_timestamp to caller
    return(0, created_at)

def md_get_last_editor_username(revision_json):
    '''
    pulls the username of the user who last edited a topic from the passed JSON
    dictionary containing information about the latest revision of a topic.
    '''
    # copy last_editor_username to local variable
    username = revision_json["username"]

    # return error code, last_editor_username to caller
    return(0, username)

def md_api_get_topic(topic_id, credentials):
    '''
    gets topic_id from the Discourse server indicated in the credentials;
    handles Discourse API wait requests and other transient errors,
    in case a large number of calls are made in a short time period
    '''

    # set rate limit error flag to True
    rate_limit_error = True

    # while rate limit error is True
    while rate_limit_error == True:

        ## do the curl call
        proc = subprocess.Popen(
            [
                "curl",
                "-s",
                "-X",
                "GET",
                "-H",
                "Api-Key: " + credentials["api_key"],
                "-H",
                "Api-Username: " + credentials["api_username"],
                "-H",
                "Content-Type: application/json",
                credentials["base_url"] + "/t/{" + str(topic_id) + "}.json",
            ],
            stdout=subprocess.PIPE,
        )

        ## read the curl result into a usable buffer
        output = proc.stdout.read()

        ## try to convert the result to json
        try:
            topic_json = json.loads(output)
        except:
            ### handle "topic doesn't exist" error
            print("error in md_api_get_topic", errno.ENODATA, ": Topic doesn't exist")
            print(output)
            sys.exit(errno.ENODATA)

        ## try to see if there's a rate_limit error
        try:
            ### if so, sleep for 20s and continue the loop
            if topic_json["error_type"] == "rate_limit":
                rate_limit_error = True
                time.sleep(20)
                continue;
        except:
            return(topic_json)


def md_api_get_latest_revision(topic_id, credentials):
    '''
    gets latest revision for topic_id from the Discourse server indicated in
    the credentials; handles Discourse API wait requests and other transient
    errors, in case a large number of calls are made in a short time period.
    '''

    # get the topic to get the post_id from it
    try:
        error, topic_json = md_api_get_topic(topic_id, credentials)
    except error != 0:
        print("error", errno.ENODATA, ": couldn't pull topic JSON for latest revision")
        sys.exit(errno.ENODATA)

    # get the post_id from the passed topic_id
    try:
       error, post_id = md_get_post_number(topic_json)
    except:
        print("error", errno.ENODATA, ": couldn't get post number for latest revision")

    # set rate limit error flag to True
    rate_limit_error = True

    # while rate limit error is True
    while rate_limit_error == True:

        ## do the curl call
        proc = subprocess.Popen(
            [
                "curl",
                "-s",
                "-X",
                "GET",
                "-H",
                "Api-Key: " + credentials["api_key"],
                "-H",
                "Api-Username: " + credentials["api_username"],
                "-H",
                "Content-Type: application/json",
                credentials["base_url"] + "/posts/" + str(post_id) + "/revisions/latest.json",
            ],
            stdout=subprocess.PIPE,
        )


        ## read the curl result into a usable buffer
        output = proc.stdout.read()

        # convert the result to json
        try:
            latest_revision_json = json.loads(output)
        ### handle "topic doesn't exist" error
        except:
            print("error", errno.ENOEXIST, ": couldn't pull latest revision")

        ## try to see if there's a rate_limit error
        try:
            ### if so, sleep for 20s and continue the loop
            if post_json["error_type"] == "rate_limit":
                rate_limit_error = True
                time.sleep(20)
                continue
        ## if no rate error
        except:
            ### return a "no-error" code and the revision json
            return(latest_revision_json)

def md_api_get_post(post_id, credentials):
    '''
    gets post_id from the Discourse server indicated in the credentials;
    handles Discourse API wait requests and other transient errors, in case a
    large number of calls are made in a short time period.
    '''
    # set rate limit error flag to True
    rate_limit_error = True

    # while rate limit error is True
    while rate_limit_error == True:

        ## do the curl call
        proc = subprocess.Popen(
            [
                "curl",
                "-s",
                "-X",
                "GET",
                "-H",
                "Api-Key: " + credentials["api_key"],
                "-H",
                "Api-Username: " + credentials["api_username"],
                "-H",
                "Content-Type: application/json",
                credentials["base_url"] + "/posts/{" + str(post_id) + "}.json",
            ],
            stdout=subprocess.PIPE,
        )


        ## read the curl result into a usable buffer
        output = proc.stdout.read()

        ## try to convert the result to json
        try:
            post_json = json.loads(output)
        ### handle "topic doesn't exist" error
        except:
            print("error", errno.ENODATA, ": couldn't get post JSON for post ID", post_id)
            sys.exit(errno.ENODATA)

        ## try to see if there's a rate_limit error
        try:
            ### if so, sleep for 20s and continue the loop
            if post_json["error_type"] == "rate_limit":
                rate_limit_error = True
                time.sleep(20)
                continue;
        ## if no rate error
        except:
            ### return a "no-error" code and the revision json
            return(post_json)

def md_api_change_title(post_id, put_buffer, new_title, credentials):
    '''
    change the title of topic_id on the Discourse server indicated in the credentials;
    handles Discourse API wait requests and other transient errors, in case a large
    number of calls are made in a short time period.
    '''
    # pad the markdown to 9000 characters to avoid a discourse bug
    put_buffer = put_buffer.ljust(9000)

    # create a dictionary buffer for the new title
    data = {}

    # load the new_title in the appropriate json key
    data["title"] = new_title
    data["raw"] = put_buffer

    # open a temp file to store the markdown ad json
    # (the put works better if it draws from a file)
    f = open("foo.json", "w")

    # convert the data dictionary to json and store it in the temp file
    f.write(json.dumps(data))

    # close the temp file
    f.close()

    # copy the auth data into individual parameters
    apikey = "Api-Key: " + credentials["api_key"]
    apiusername = "Api-Username: " + credentials["api_username"]

    # build the appropriate URL based on the calling sequence
    url = credentials["base_url"] + "/posts/{" + str(post_id) + "}.json"

    # set rate_limit_error flag
    rate_limit_error = True

    # while rate limit error is True
    while rate_limit_error == True:

        ## use the curl command to post the new_title to the post on discourse,
        ## and read the result into a usable return buffer
        proc= subprocess.Popen(
            [
                "curl",
                "-s",
                "-X",
                "PUT",
                url,
                "-H",
                apikey,
                "-H",
                apiusername,
                "-H",
                "Content-Type: application/json",
                "-d",
                "@foo.json",
            ],
            stdout=subprocess.PIPE,
        )

        ## read the curl result into a usable buffer
        output = proc.stdout.read()

        ## try to convert the result to json
        try:
            post_json = json.loads(output)
        ### handle "topic doesn't exist" error
        except:
            print("error", errno.ENODATA, ": post ", post_id, "doesn't exist when trying to change title")
            sys.exit(errno.ENODATA)

        ## try to see if there's a rate_limit error
        try:
            ### if so, sleep for 20s and continue the loop
            if post_json["error_type"] == "rate_limit":
                rate_limit_error = True
                time.sleep(20)
                continue;
        ## if no rate error
        except:
            ### remove the temporary json file
            os.remove("foo.json")
            ### return a clear error and the post_json
            return(post_json)

def md_api_delete_topic(topic_number, credentials):
    '''
    deletes a discourse topic with the passed topic number.  accepts: a topic number (integer) and a set of API credentials (dictionary); returns nothing. 
    '''

    # copy the auth data into individual parameters
    apikey = "Api-Key: " + credentials["api_key"]
    apiusername = "Api-Username: " + credentials["api_username"]

    # build the appropriate URL based on the calling sequence
    url = credentials["base_url"] + "/t/{" + topic_number + "}.json"

    ## use the curl command to post put_buffer to the post on discourse,
    ## and read the result into a usable return buffer
    proc= subprocess.Popen(
        [
            "curl",
            "-s",
            "-X",
            "DELETE",
            url,
            "-H",
            apikey,
            "-H",
            apiusername,
        ],
        stdout=subprocess.PIPE,
    )

def md_api_new_topic(title, markdown, category, credentials):
    '''
    creates a new discourse topic with the passed title, and posts the passed markdown to the new topic; accepts: a topic title (string), a buffer containing the markdown to push, a category for the topic, and a set of API credentials (dictionary); returns: the topic number of the newly-created topic.
    '''

    # pad the markdown to 9000 characters to avoid a discourse bug
    # pad the markdown to 9000 characters to avoid a discourse bug
    put_buffer = markdown.ljust(9000)

    # create a dictionary buffer for the put_buffer
    data = {}

    # load the put_buffer in the appropriate json key
    data["title"] = title
    data["raw"] = put_buffer
    data["category"] = category

    # open a temp file to store the markdown ad json
    # (the put works better if it draws from a file)
    f = open("foo.json", "w")

    # convert the data dictionary to json and store it in the temp file
    f.write(json.dumps(data))

    # close the temp file
    f.close()

    # copy the auth data into individual parameters
    apikey = "Api-Key: " + credentials["api_key"]
    apiusername = "Api-Username: " + credentials["api_username"]

    # build the appropriate URL based on the calling sequence
    url = credentials["base_url"] + "/posts.json"

    # set rate_limit_error flag
    rate_limit_error = True

    # while rate limit error is True
    while rate_limit_error == True:

        ## use the curl command to post put_buffer to the post on discourse,
        ## and read the result into a usable return buffer
        proc= subprocess.Popen(
            [
                "curl",
                "-s",
                "-X",
                "POST",
                url,
                "-H",
                apikey,
                "-H",
                apiusername,
                "-H",
                "Content-Type: application/json",
                "-d",
                "@foo.json",
            ],
            stdout=subprocess.PIPE,
        )

        ## read the curl result into a usable buffer
        output = proc.stdout.read()

        ## try to convert the result to json
        try:
            post_json = json.loads(output)
        ### handle "topic doesn't exist" error
        except:
            print("error", errno.ENODATA, ": topic not created")
            sys.exit(errno.ENODATA)

        ## try to see if there's a rate_limit error
        try:
            ### if so, sleep for 20s and continue the loop
            if post_json["error_type"] == "rate_limit":
                rate_limit_error = True
                time.sleep(20)
                continue;
        ## if no rate error
        except:
            ### remove the temporary json file
            os.remove("foo.json")
            ### return a clear error and the post_json
            return(post_json["topic_id"])
    
def md_api_put_post(post_id, markdown, credentials):
    '''
    puts a new version of topic_id the Discourse server indicated in the credentials;
    handles Discourse API wait requests and other transient errors, in case a large
    number of calls are made in a short time period.
    '''

    debug = False
    
    if debug == True:
        print("md_api_put_post::entering, post id", post_id)
    
    # pad the markdown to 9000 characters to avoid a discourse bug
    put_buffer = markdown.ljust(9000)
    if debug == True:
        print("md_api_put_post::just padded put_buffer for post id", post_id)

    # create a dictionary buffer for the put_buffer
    data = {}
    if debug == True:
        print("md_api_put_post::just created dict buffer for post id", post_id)

    # load the put_buffer in the appropriate json key
    data["raw"] = put_buffer
    if debug == True:
        print("md_api_put_post::just loaded put_buffer for post id", post_id)

    # open a temp file to store the markdown ad json
    # (the put works better if it draws from a file)
    f = open("foo.json", "w")
    if debug == True:
        print("md_api_put_post::opened foo.json for post id", post_id)

    # convert the data dictionary to json and store it in the temp file
    f.write(json.dumps(data))
    if debug == True:
        print("md_api_put_post::wrote to foo.json for post id", post_id)

    # close the temp file
    f.close()
    if debug == True:
        print("md_api_put_post::closed foo.json for post id", post_id)

    # copy the auth data into individual parameters
    apikey = "Api-Key: " + credentials["api_key"]
    apiusername = "Api-Username: " + credentials["api_username"]
    if debug == True:
        print("md_api_put_post::copied creds for post id", post_id)

    # build the appropriate URL based on the calling sequence
    url = credentials["base_url"] + "/posts/{" + str(post_id) + "}.json"
    if debug == True:
        print("md_api_put_post::formulated URL for post id", post_id)

    # set rate_limit_error flag
    rate_limit_error = True
    if debug == True:
        print("md_api_put_post::just init'd rate_limit_error for post_id", post_id)

    # while rate limit error is True
    while rate_limit_error == True:
        if debug == True:
            print("md_api_put_post::top of while rate_limit_error loop")

        ## use the curl command to post put_buffer to the post on discourse,
        ## and read the result into a usable return buffer
        proc= subprocess.Popen(
            [
                "curl",
                "-s",
                "-X",
                "PUT",
                url,
                "-H",
                apikey,
                "-H",
                apiusername,
                "-H",
                "Content-Type: application/json",
                "-d",
                "@foo.json",
            ],
            stdout=subprocess.PIPE,
        )
        if debug == True:
            print("md_api_put_post::right after curl for post id", post_id)

        ## read the curl result into a usable buffer
        output = proc.stdout.read()
        if debug == True:
            print("md_api_put_post::after proc.stdout.read()")

        ## try to convert the result to json
        try:
            if debug == True:
                print("md_api_put_post::trying to convert post_json to json")
            post_json = json.loads(output)

        ### handle "topic doesn't exist" error
        except:
            if debug == True:
                print("error", errno.ENODATA, ": post", post_id, "doesn't exist")
            sys.exit(errno.ENODATA)

        ## try to see if there's a rate_limit error
        try:
            if debug == True:
                print("md_api_put_post :: trying rate_limit_error")

            ### if so, sleep for 20s and continue the loop
            if post_json["error_type"] == "rate_limit":
                rate_limit_error = True
                if debug == True:
                    print("md_api_put_post::rate_limit_error")
                time.sleep(20)
                continue;
        ## if no rate error
        except:
            ### remove the temporary json file
            os.remove("foo.json")
            ### return a clear error and the post_json
            return(post_json)

def md_api_has_been_updated(topic_id, interval, credentials):
    '''
    checks to see whether a topic has been updated in the last interval hours
    '''

    # get the last revision for the specified topic
    error, last_revision_json = md_api_get_latest_revision( topic_id, credentials )

    # extract the timestamp from the last revision information
    error, last_rev_timestamp = md_get_last_edit_timestamp(last_revision_json)

    # fix the timestamp so it can be compared with current system time
    last_rev_timestamp = last_rev_timestamp.replace("T"," ")
    last_rev_timestamp = last_rev_timestamp.replace("Z"," ")

    # get the current timestamp, consistent with the Discourse server
    ts = datetime.datetime.utcnow()

    # subtract "interval" from the current timestamp
    new_time = ts - timedelta(hours=interval)

    # compare the subtracted timestamp to the last revision timesstamp
    if str(new_time) < last_rev_timestamp:
        return True
    else:
        return False

def md_get_credentials(credential_file_path):
    '''
    reads API URL and credentials from a specified file into a list for use with
    the various API calls above
    '''

    # find credential file by attempting to open it
    try:
        cfile = open(credential_file_path, "r")
    except:
        print("error", errno.ENOFILE, ": can't open credential file", credential_file_path)
        sys.exit(errno.ENOFILE)

    # read credential file into a list, using the YAML parser
    credentials = load(cfile, Loader=Loader)

    # close the credential file
    cfile.close()

    # return credentials
    return(credentials)

def md_get_post_number(topic_json):
    '''
    pulls the post number for the first post in a topic (needed for most topic
    modifications) from the passed JSON dictionary containing information about
    a topic.
    '''

    # copy post_number to local variable
    try:
        post_id = topic_json["post_stream"]["posts"][0]["id"]
    except:
        print("error", errno.ENODATA, ": post number", post_id, "doesn't exist")
        sys.exit(errno.ENODATA)

    # return post_nubmer to caller
    return(post_id)

def md_get_markdown_content(post_json):
    '''
    pulls the actual topic markdown content from the passed JSON dictionary
    containing information about a post.
    '''
    # copy raw component to local variable
    try:
        markdown = post_json["raw"]
    except:
        print("error", errno.ENODATA, ": markdown content doesn't exist")
        sys.exit(errno.ENODATA)

    # return error code, markdown_content to caller
    return(markdown)

def md_is_later_than(timestamp_1, timestamp_2):
    '''
    compares two Discourse timestamps as strings and returns True if the first
    passed timestamp is later than the second.  Discourse timestamps in JSON payloads
    are formatted as strings in a way that does not require converting them to
    datetime types to compare them.
    '''

    # return_value = ts1 > ts2
    return(timestamp_1 > timestamp_2)

def md_is_earlier_than(timestamp_1, timestamp_2):
    '''
    compares two Discourse timestamps as strings and returns True if the first
    passed timestamp is earlier than the second.
    '''

    # return_value = ts1 < ts2
    return(timestamp_1 < timestamp_2)

def md_is_identical_to(timestamp_1, timestamp_2):
    '''
    compares to Discourse timestamps as strings and returns True if they
    are identical.
    '''

    # return_value = ts1 ==n ts2
    return(timestamp_1 == timestamp_2)
