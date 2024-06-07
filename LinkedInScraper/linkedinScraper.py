import csv
import logging
import requests
import pandas as pd
import datetime
import os
from leadarScraper import searchLeadar
from dotenv import load_dotenv


def getLinkedInData(linkedin_url):
    load_dotenv()
    api_key = os.getenv("NUBELA_API_KEY_TWO")
    headers = {'Authorization': 'Bearer ' + api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    params = {'linkedin_profile_url': linkedin_url}

    response = requests.get(api_endpoint, params=params, headers=headers)
    return response


def cleanData(data):
    def format_date(date):
        if date:
            return f"{date['day']}/{date['month']}/{date['year']}"
        else:
            return None

    # Clean experiences data
    if 'experiences' in data:
        experiences = [
            {
                "company": exp.get('company'),
                "company_linkedin_profile_url": exp.get('company_linkedin_profile_url'),
                "description": exp.get('description'),
                "date": format_date(exp.get('starts_at')),
                "title": exp.get('title')
            }
            for exp in data['experiences']
        ]
    else:
        experiences = []

    # Clean education data
    if 'education' in data:
        education = [
            {
                "degree_name": edu.get('degree_name'),
                "field_of_study": edu.get('field_of_study'),
                "description": edu.get('description'),
                "date_start": format_date(edu.get('starts_at')),
                "date_end": format_date(edu.get('ends_at'))
            }
            for edu in data['education']
        ]
    else:
        education = []

    # Clean volunteer data
    if 'volunteer_work' in data:
        volunteering = [
            {
                "company": vol.get('company'),
                "company_linkedin_profile_url": vol.get('company_linkedin_profile_url'),
                "description": vol.get('cause'),
                "date_start": format_date(vol.get('starts_at')),
                "date_end": format_date(vol.get('ends_at')),
                "volunteer_activity": vol.get('title')
            }
            for vol in data['volunteer_work']
        ]
    else:
        volunteering = []

    # Clean articles data
    if 'articles' in data:
        articles = [
            {
                "title": article.get('title'),
                "published_date": format_date(article.get('published_date')),
                "author": article.get('author')
            }
            for article in data['articles']
        ]
    else:
        articles = []

    # Clean projects data
    if 'accomplishment_projects' in data:
        projects = [
            {
                "title": project.get('title'),
                "description": project.get('description'),
                "starts_at": format_date(project.get('starts_at')),
                "ends_at": format_date(project.get('ends_at'))
            }
            for project in data['accomplishment_projects']
        ]
    else:
        projects = []

    # Clean publication data
    if 'accomplishment_publications' in data:
        publications = [
            {
                "name": publication.get('name'),
                "publisher": publication.get('publisher'),
                "description": publication.get('description'),
                "date_published": format_date(publication.get('published_on'))
            }
            for publication in data['accomplishment_publications']
        ]
    else:
        publications = []

    # Clean honor awards data
    if 'accomplishment_honors_awards' in data:
        awards = [
            {
                "title": award.get('title'),
                "issuer": award.get('issuer'),
                "issued_on": format_date(award.get('issued_on')),
                "description": award.get('description')
            }
            for award in data['accomplishment_honors_awards']
        ]
    else:
        awards = []

    if 'activities' in data:
        activities = [
            {
                "title": activity.get('title'),
                "link": activity.get('link'),
                "status": activity.get('activity_status')
            }
            for activity in data['activities']
        ]
    else:
        activities = []

    cleaned_data_dict = {
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name'),
        "full_name": data.get('full_name'),
        "public_identifier": data.get('public_identifier'),
        "headline": data.get('headline'),
        "occupation": data.get('occupation'),
        "location": {
            "country": f"{data.get('country_full_name')} ({data.get('country')})",
            "city": data.get('city'),
            "state": data.get('state')
        },
        "activities": activities,
        "languages": data.get('languages'),
        "followers": data.get('follower_count'),
        "connections": data.get('connections'),
        "biography": data.get('summary'),
        "recent_experiences": experiences,
        "education": education,
        "volunteering": volunteering,
        "articles": articles,
        "projects": projects,
        "awards": awards,
        "publications": publications
    }
    return cleaned_data_dict


def createExcelFile(input_csv):
    df = pd.read_csv(input_csv)
    excel_file = f'{input_csv[:-4]}.xlsx'
    df.to_excel(excel_file, index=False)


def getFileDetails(input_file, linkedin_url_header):
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")

    # Define output folder path
    output_folder = os.path.dirname(input_file)
    log_file = os.path.join(output_folder, 'file_details.log')

    # Configure logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    raw_fieldnames = ["state", "accomplishment_test_scores", "accomplishment_organisations",
                      "summary", "certifications", "groups", "birth_date", "personal_emails",
                      "inferred_salary", "accomplishment_courses", "volunteer_work",
                      "background_cover_image_url", "experiences", "skills", "people_also_viewed",
                      "accomplishment_honors_awards", "interests", "activities",
                      "accomplishment_patents", "accomplishment_projects", "city",
                      "recommendations", "industry", "extra", "country_full_name",
                      "similarly_named_profiles", "gender", "profile_pic_url",
                      "accomplishment_publications", "personal_numbers", "country",
                      "follower_count", "languages", "public_identifier", "first_name",
                      "last_name", "connections", "occupation", "headline", "articles",
                      "full_name", "education"]

    cleaned_fieldnames = ["first_name", "last_name", "full_name", "public_identifier",
                          "headline", "occupation", "location", "languages", "followers",
                          "connections", "biography", "recent_experiences", "education",
                          "volunteering", "articles", "projects", "awards", "publications", 'facebook', "gender",
                          "numbers", "industry", "salary", "skills", "twitter", "birthday", "interests", "emails",
                          "activities"]

    raw_file = os.path.join(output_folder,
                            f'{os.path.splitext(os.path.basename(input_file))[0]}_raw_data_{current_date}.csv')
    cleaned_file = os.path.join(output_folder,
                                f'{os.path.splitext(os.path.basename(input_file))[0]}_cleaned_{current_date}.csv')

    # Check if output files exist
    if os.path.isfile(raw_file) and os.path.isfile(cleaned_file):
        try:
            last_processed_row = pd.read_csv(cleaned_file).tail(1).index.item() + 1
        except Exception as e:
            logging.error(f"Error reading cleaned file: {e}")
            last_processed_row = 0
    else:
        last_processed_row = 0

    logging.info(f"Beginning Advancing Lead Data on File: {input_file}.")
    # Iterate through each row in the input file starting from the last processed row
    try:
        with open(raw_file, 'a', newline='', encoding='utf-8') as raw_csv, \
                open(cleaned_file, 'a', newline='', encoding='utf-8') as cleaned_csv:

            raw_writer = csv.DictWriter(raw_csv, fieldnames=raw_fieldnames)
            cleaned_writer = csv.DictWriter(cleaned_csv, fieldnames=cleaned_fieldnames)

            if last_processed_row == 0:
                raw_writer.writeheader()
                cleaned_writer.writeheader()

            df = pd.read_csv(input_file)

            for index, row in df.iloc[last_processed_row:].iterrows():
                linkedin_profile_url = row[linkedin_url_header]
                if not linkedin_profile_url:
                    logging.warning("Skipping row: LinkedIn URL is missing")
                    continue
                logging.info(f"Running for LinkedIn URL: {linkedin_profile_url}")
                response = getLinkedInData(linkedin_profile_url)
                if response.status_code != 200:
                    logging.error(f"Failed to fetch data from LinkedIn URL: {linkedin_profile_url}")
                    continue
                try:
                    data = response.json()
                except Exception as e:
                    logging.error(f"Error parsing JSON data: {e}")
                    continue

                # Clean data and search Leadar
                cleaned_data = cleanData(data)
                additional_info = searchLeadar(name=cleaned_data['full_name'], linkedin_url=linkedin_profile_url)
                if additional_info['success']:
                    logging.info("Collected additional info.")
                    for key, value in additional_info['data'].items():
                        if key not in ['name', 'linkedin', 'job_title', 'location']:
                            cleaned_data[key] = value
                else:
                    logging.info("No additional info found.")
                    logging.info(additional_info['message'])

                # Write raw data to CSV
                raw_writer.writerow(data)
                # Write cleaned data to CSV
                cleaned_writer.writerow(cleaned_data)
        logging.info("File details processing completed.")
        createExcelFile(cleaned_file)

    except Exception as e:
        logging.error(f"Error processing file details: {e}")
