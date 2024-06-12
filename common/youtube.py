#!/usr/bin/python

import httplib2
import os
import random
import sys
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


class YoutubeArgs:
    def __init__(self, video_path: str, title: str, description: str, category: int, keywords: str, privacy_status="private", auth_host_name="localhost", auth_host_port=[8080, 8090], logging_level="ERROR", noauth_local_webserver=False):
        self.file = video_path
        self.title = title
        self.description = description
        self.category = str(category)
        self.keywords = keywords
        self.privacy_status = privacy_status
        self.auth_host_name = auth_host_name
        self.auth_host_port = auth_host_port
        self.logging_level = logging_level
        self.noauth_local_webserver = noauth_local_webserver





class YoutubeUploader:
    def __init__(self, args: YoutubeArgs ):
        # Explicitly tell the underlying HTTP transport library not to retry, since
        # we are handling retry logic ourselves.
        httplib2.RETRIES = 1
        self.MAX_RETRIES = 10
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        self.CLIENT_SECRETS_FILE = "appdata/restricted/client_secret.json"
        self.UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
        self.API_SERVICE_NAME = "youtube"
        self.API_VERSION = "v3"
        self.ARGS = args
        # for categories list: https://developers.google.com/youtube/v3/docs/videoCategories/list
        self.VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")



        self
        with open("appdata/missing_client_secret_msg.txt", 'r') as file:
            self.MISSING_CLIENT_SECRETS_MESSAGE = file.read().replace("[FILE_PATH]", self.CLIENT_SECRETS_FILE)


    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
            scope=self.UPLOAD_SCOPE,
            message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage(f"{sys.argv[0]}-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, self.ARGS)

        return build(self.API_SERVICE_NAME, self.API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.)
    def initialize_upload(self, youtube, chunksize=-1):

        body=dict(
            snippet=dict(
                title=self.ARGS.title,
                description=self.ARGS.description,
                tags=self.ARGS.keywords,
                categoryId=self.ARGS.category
            ),
            status=dict(
                privacyStatus=self.ARGS.privacy_status
            )
        )

        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(self.ARGS.file, chunksize=chunksize, resumable=True)
        )

        self.resumable_upload(insert_request)


    # Implements an exponential backoff strategy to resume a failed upload.

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print("Uploading File...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
                    else:
                        exit(f"The upload failed with an unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > self.MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)

    def run(self):
        if not os.path.exists(self.ARGS.file):
            print(f"Error: {self.ARGS.file} does not exist.")

        youtube = self.get_authenticated_service()
        try:
            self.initialize_upload(youtube)
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")



