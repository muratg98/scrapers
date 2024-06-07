import json
import brotli
import requests
import urllib3

headers = {
    "Host": "www.yelp.co.uk",
    "Connection": "keep-alive",
    'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'sec-ch-ua-platform': 'Windows',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'content-type': 'application/json',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.yelp.co.uk/search?find_desc=Eyebrows&find_loc=London',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cookie': 'Cookie: OptanonAlertBoxClosed=2023-10-19T12:53:18.455Z; bse=088a91dc222d4cf38b6926eaed48bbbd; used_locale_selector=t; wdi=2|F8ADB52B45202145|0x1.94c86c19efb87p+30|e5623973ba1061f5; xcj=1|nTBbOR-tEPsszz-KgQBjPykYzTwfFoH4elRkpm8MSAc; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+20+2023+09%3A31%3A09+GMT%2B0100+(British+Summer+Time)&version=202308.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=bb81de7f-9b3d-4840-b65d-5f476419c9ab&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0&iType=2&geolocation=GB%3BENG&AwaitingReconsent=false'
}


def retrieve_companies(keyword, location, page=0):
    base_url = 'https://www.yelp.co.uk/search/snippet'
    results = []

    while True:
        url = f'{base_url}?find_desc={keyword}&find_loc={location}&start={page}&parent_request_id=b371d4b505bc1f50&request_origin=user'
        urllib3.disable_warnings()
        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"Error: Request failed with status code {response.status_code}")
            print(f"Error Message: {response.text}")
            break
        if not response.text:
            print("Error: Response is empty.")
            break
        try:
            response.json()
        except ValueError:
            content_encoding = response.headers.get('Content-Encoding')
            if content_encoding == 'br':
                compressed_data = response.content
                response = brotli.decompress(compressed_data)
        data = process_data(response)
        if not data:
            print(f"No results found in the response.\n{response.text}\n Exiting.")
            page += 10
            break
        results.append(data)
        # Increment the page number
        page += 10
    print(results)
    return results


def process_data(response):
    try:
        data = response.json().get("searchPageProps", {}).get("mainContentComponentsListProps", [])
    except (KeyError, json.JSONDecodeError):
        print("Error: Invalid or missing data in the response.")
        return {}

    businessInfo = {}
    for item in data:
        if isinstance(item, dict) and item.get("bizId") is not None:
            business = item.get("searchResultBusiness", {})
            businessInfo["name"] = business.get("name", "N/A")
            businessInfo["phone"] = business.get("phone", "N/A")
            website = business.get("website")
            if isinstance(website, dict):
                businessInfo["website"] = website.get("href", "N/A")
            else:
                businessInfo["website"] = "N/A"
            businessInfo["location"] = business.get("neighborhoods", "N/A")
            businessInfo["yelpRating"] = business.get("rating", "N/A")
    # TODO: Log the data + send to the database
    return businessInfo





# Example usage:
keyword = 'Burgers'
location = 'London'
companies = retrieve_companies(keyword, location)

# Now 'companies' will contain the data retrieved from all the pages.
