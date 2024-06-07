import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import re
from zenrows import ZenRowsClient


def searchLeadar(name, linkedin_url):
    query = f"{linkedin_url} site:leadar.ai"
    name_words = name.split()
    profile_data = {
        "name": "",
        "job_title": "",
        "industry": "",
        "emails": [],
        "numbers": [],
        "location": "",
        "gender": "",
        "salary": "",
        "birthday": "",
        "linkedin": "",
        "facebook": "",
        "twitter": "",
        "skills": [],
        "interests": []
    }
    try:
        with DDGS() as ddgs:
            r = [r for r in ddgs.text(query, backend="html", max_results=3)]
            if not r:
                return {
                    "success": False,
                    "message": "No search results found."
                }
            for result in r:
                url = result.get('href')
                if not url:
                    print("Invalid result:", result)
                    continue
                if all(word.lower() in result.get('title', '').lower() for word in name_words) and re.match(
                        r'^https:\/\/www\.leadar\.ai\/profile\/[a-f0-9]{24}$', url):
                    load_dotenv()
                    zen_api_key = os.getenv("ZENROWS_API_KEY")
                    client = ZenRowsClient(zen_api_key)
                    response = client.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, features="lxml")
                        name = soup.find('span', itemprop='name').get_text(strip=True)
                        profile_data["name"] = name
                        job_title = soup.find('span', itemprop='jobTitle').get_text(strip=True)
                        profile_data["job_title"] = job_title
                        industry = soup.find('div', class_='profile-heading-about')\
                            .find('b', string='industry:')
                        if industry:
                            profile_data["industry"] = industry.next_sibling.text.strip()
                        else:
                            profile_data["industry"] = "Unknown"
                        profile_items = soup.find_all(class_='profile-section-item')
                        for item in profile_items:
                            title = item.find(class_='profile-section-item__title').get_text(strip=True)
                            if title == "Email addresses":
                                emails = item.find_all(itemprop="email")
                                email_list = [email.get_text(strip=True) for email in emails]
                                profile_data["emails"] = email_list
                            elif title == "Phone numbers":
                                phones = item.find_all(itemprop="telephone")
                                phone_list = [phone.get_text(strip=True) for phone in phones]
                                profile_data["numbers"] = phone_list
                            elif title == "Location":
                                location = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["location"] = location
                            elif title == "Gender":
                                gender = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["gender"] = gender
                            elif title == "Inferred Salary":
                                salary = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["salary"] = salary
                            elif title == "Date of birth":
                                birthday = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["birthday"] = birthday
                            elif title == "LinkedIn":
                                linkedin = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["linkedin"] = linkedin
                            elif title == "Facebook":
                                facebook = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["facebook"] = facebook
                            elif title == "Twitter":
                                twitter = item.find(class_='profile-section-item__text').get_text(strip=True)
                                profile_data["twitter"] = twitter
                            else:
                                continue

                        skills_section = soup.find('section', class_='profile-skills')
                        if skills_section:
                            skills = [tag.get_text(strip=True) for tag in skills_section.find_all('p', class_='tag-item')]
                            profile_data['skills'] = skills
                        else:
                            profile_data['skills'] = []

                        interests_section = soup.find('section', class_='profile-interests')
                        if interests_section:
                            interests = [tag.get_text(strip=True) for tag in interests_section.find_all('p', class_='tag-item')]
                            profile_data['interests'] = interests
                        else:
                            profile_data['interests'] = []

                        return {
                            "success": True,
                            "data": profile_data
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Failed to retrieve profile data."
                        }
                else:
                    continue
            return {
                "success": False,
                "message": "No valid Leadar profiles found for the given name and LinkedIn URL."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
