# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from datetime import date
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload
import requests
import shutil

load_dotenv()

CHANNEL_ID = os.getenv('yt_channel_id')
switchboard_api_key = os.getenv('switchboard')

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
request_url = "https://api.canvas.switchboard.ai"

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YathartYTClientSecret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    ### Get videoId list
    requestVidId = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        order="date"
    )
    responseVidId = requestVidId.execute()
    print(responseVidId)
    print(f"\n\n\n\n\n")
    print(responseVidId['items'][0]['id']['videoId'])

    ### Get videoId list
    for item in responseVidId['items']:

        vidId = item['id']['videoId']

        print(f"Vidid: {vidId}")

        ### Get statistics
        requestStats = youtube.videos().list(
            part="statistics",
            id=vidId
        )
        responseStats = requestStats.execute()

        # Format & display statistics
        for item in responseStats['items']:
            views = item['statistics']['viewCount']
            likes = item['statistics']['likeCount']
            dislikes = item['statistics']['dislikeCount']

        # Check to prevent Divide by Zero Error.
        if (float(likes) + float(dislikes)) == 0:
            ratio = 0
        else:
            ratio = round((float(likes) / (float(likes) + float(dislikes)) * 100), 2)

        # Getting the current date, to show when the counter was last updated.
        today = date.today()
        currentDate = today.strftime("%b-%d-%Y")

        # Creating the Switchboard response payload
        switchboard_response_payload = {
            "template": "youtube-dislikes",
            "sizes" : [
                {
                    "width" : 1280,
                    "height" : 720
                }],
            "elements": {
                "image1": {
                    "url": "https://tinyurl.com/2stabcjp"
                },
                "likes-count" : {
                    "text" : f"{likes}"
                },
                "dislikes-count" : {
                    "text" : f"{dislikes}"
                },
                "ratio" : {
                    "text" : f"{ratio}%"
                }
            }
        }

        # Send the payload to Switchboard

        print(switchboard_response_payload)

        # Send the payload to Switchboard
        swb_response = requests.post(
            request_url,
            json=switchboard_response_payload,
            headers={
                "X-API-Key": f"{switchboard_api_key}",
                "Content-Type": "application/json"
            }
        )
        # Parsing the URL, and printing it
        url = swb_response.json()['sizes'][0]['url']
        print(f"url : {url}")

        # Getting the URL
        response = requests.get(url)

        # Checking on the basis of status code, and it not 200, storing in file
        if response.status_code == 200:
            with open(f'{vidId}.png', 'wb')as f:
                f.write(response.content)
        else:
            print(f"Error. Http response code : {response.status_code}")
            seconds = time.time()
            local_time = time.ctime(seconds)
            with open(f"Request_response_{local_time}.txt", "w") as f:
                f.write(f"{response.content}")

        # Calling the Thumbnail set method
        thumbnail_update_request = youtube.thumbnails().set(
            videoId=vidId,
            media_body=MediaFileUpload(f"{vidId}.png", resumable=True)
        )
        thumbnail_update_response = thumbnail_update_request.execute()
        print(thumbnail_update_response)

if __name__ == "__main__":
    main()