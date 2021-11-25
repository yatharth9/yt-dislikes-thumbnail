# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

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
#SEARCH_TERMS = os.getenv('SEARCH_TERMS')

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

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

        # Generating image from memegen
        memegen_base_url =  f"https://api.memegen.link/images/custom/Views:-{views}/Likes:-{likes}_Dislikes:-{dislikes}~nRatio:-{ratio}-~nLast-Updated:-{currentDate}?background=http://www.gstatic.com/webp/gallery/1.png"
        response = requests.get(memegen_base_url, stream=True)
        
        # Storing it in persistent memory
        with open(f'{vidId}.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        
        # Calling the Thumbnail set method
        thumbnail_update_request = youtube.thumbnails().set(
            videoId=vidId,
            media_body=MediaFileUpload(f"{vidId}.png", resumable=True)
        )
        thumbnail_update_response = thumbnail_update_request.execute()
        print(thumbnail_update_response)

if __name__ == "__main__":
    main()
