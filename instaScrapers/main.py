import requests
import pprint
from datetime import datetime
import pandas as pd

headers = {
    'Host': 'www.instagram.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'X-IG-WWW-Claim': '0',
    'sec-ch-ua-platform-version': '10.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'dpr': '1',
    'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.225", "Google Chrome";v="120.0.6099.225"',
    'sec-ch-prefers-color-scheme': 'light',
    'X-CSRFToken': 'j1L9SzWR2GwI4PXrzMons5',
    'sec-ch-ua-platform': "Windows",
    'X-IG-App-ID': '936619743392459',
    'sec-ch-ua-model': "",
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'viewport-width': '1141',
    'Accept': '*/*',
    'X-ASBD-ID': '129477',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.google.co.uk/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en;q=0.9',
}


def getClientInsta(account_name):
    endpoint = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={account_name}&hl=en'
    response = requests.get(url=endpoint, headers=headers)
    data = response.json()["data"]["user"]
    user_posts = data['edge_owner_to_timeline_media']['edges']
    posts = [
        {
            'caption': post['node']['edge_media_to_caption']['edges'][0]['node']['text'],
            'image': post['node']['display_url'],
            'comments': post['node']['edge_media_to_comment']['count'],
            'likes': post['node']['edge_liked_by'],
            'is_video': post['node']['is_video'],
            'owner': post['node']['owner']['username'],
            'date': (datetime.utcfromtimestamp(post['node']['taken_at_timestamp'])).strftime('%Y-%m-%d')
        }
        for post in user_posts
    ]
    print(f"POSTS FOUND: {len(posts)}")
    # user_insta_data = {
    #     'bio': user_bio,
    #     'category': user_category,
    #     'following': user_following,
    #     'followers': user_followers,
    #     'total_posts': user_num_of_post,
    #     'full_name': user_full_name,
    #     'posts': latest_posts
    # }
    return posts


account_name = "hello"
info = getClientInsta(account_name)

