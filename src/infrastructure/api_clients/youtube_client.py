#!/usr/bin/python

import httplib2
import os
import random
import sys
import time
from moviepy.editor import VideoFileClip, CompositeVideoClip

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
    def __init__(self, args: YoutubeArgs, aspect=(9,16)):
        # Explicitly tell the underlying HTTP transport library not to retry, since
        # we are handling retry logic ourselves.
        httplib2.RETRIES = 1
        self.MAX_RETRIES = 10
        self.RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
        self.RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
        self.CLIENT_SECRETS_FILE = "data/restricted/google_secret.json"
        self.UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
        self.API_SERVICE_NAME = "youtube"
        self.API_VERSION = "v3"
        self.VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

        # Force Aspect ratio
        filename = args.file.split(".")
        modded_filepath = f"{filename[0]}_modded.{filename[1]}"
        print(modded_filepath)
        self.force_aspect_ratio(args.file, output_path=f"{modded_filepath}", aspect_ratio=aspect)

        # Edit args before making an instance variable
        args.file = modded_filepath
        args.title += " #shorts"
        args.description += " #shorts"
        args.keywords += ", shorts"
        self.ARGS = args

        with open("data/missing_client_secret_msg.txt", 'r') as file:
            self.MISSING_CLIENT_SECRETS_MESSAGE = file.read().replace("[FILE_PATH]", self.CLIENT_SECRETS_FILE)


    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.CLIENT_SECRETS_FILE,
            scope=self.UPLOAD_SCOPE,
            message=self.MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage(f"data/restricted/google-oauth2.json")
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

    def force_aspect_ratio(self, filepath: str, output_path="", aspect_ratio=(9, 16)):
        if output_path == "":
            output_path = filepath

        print(f"\nChanging {filepath.split('/')[-1]} aspect ratio to {aspect_ratio[0]}:{aspect_ratio[1]}...")
        print(f"Outputting cropped video to file: {output_path}...")
        clip = VideoFileClip(filepath)
        original_width, original_height = clip.size
        target_ratio = aspect_ratio[0] / aspect_ratio [1]

        if (original_width / original_height) > target_ratio:
            target_height = original_height
            target_width = int(target_height * target_ratio)
        else:
            target_width = original_width
            target_height = int(target_width / target_ratio)

        cropped_clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=target_width, height=target_height)

        cropped_clip.write_videofile(output_path, codec='libx264', fps=clip.fps, preset="slow")

