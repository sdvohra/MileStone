import json
import random
from watson_developer_cloud import AlchemyLanguageV1
import requests

data = {'term':'attractions', 'latitude': '37.3382', 'longitude' : '-121.8863'}
headers = {'Authorization' : "Bearer EEQYq44chnPYd1GcTAaL9dkbTrq2Dg4hgZrOV6ddlKCpesirGDZifOkVQ1g4nlnU_lS0n3NRjh_0TYKC-tOpk3HfjPsEBoirvHpwYBL-ydRHced3Kcy9HtdEaasnWHYx"}

r = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params = data)
response = r.json()
businesses = response['businesses']
urls = [biz['url'] for biz in businesses]

url_to_keywords = {}
alchemy_language = AlchemyLanguageV1(api_key='84e9ae395824ae2cf3e063260adfc73c95c93261')
for link in urls:
    excess_data = alchemy_language.taxonomy(url=link)
    data = [tag["label"] for tag in excess_data['taxonomy']]
    url_to_keywords[link] = data

def parse_keywords(lst):
    keywords = []
    for phrase in lst:
        keywords += phrase.split('/')
    keywords = [x for x in keywords if x != '']
    return keywords

total_categories = []
for url in urls:
    total_categories.extend(parse_keywords(url_to_keywords[url]))
    url_to_keywords[url] = parse_keywords(url_to_keywords[url])

occurrences = {}
for category in total_categories:
    if category in occurrences:
        occurrences[category] += 1
    else:
        occurrences[category] = 1

max_cat = []
for i in range(10):
    max_cat += [max(occurrences, key = lambda x: occurrences[x])]
    occurrences.pop(max_cat[i])

ranks = {}
for cat in max_cat:
    ranks[cat] = 0

### Original Question: randomly generate 2
choice1, choice2 = random.randrange(0, 10), random.randrange(0, 10)
while choice2 == choice1:
    choice2 = random.randrange(0, 10)
choice1_url, choice2_url = urls[choice1], urls[choice2]

keep_playing = True

while keep_playing:
    try:
        ### Which one does user want?
        choice = input(businesses[choice1]['name'] + " or " + businesses[choice2]['name'] + "? ")  # expect 1 or 2
        final_url = ""
        if choice == '1':
            print('Destination: ' + businesses[choice1]['name'])
            final_url = choice1_url
        else:
            print('Destination: ' + businesses[choice2]['name'])
            final_url = choice2_url

        rating = input('What did ya think? (1) Great!, (2) Not so great :/ ')
        print("Thanks for the feedback! Calculating new milestones...")

        update_keywords = url_to_keywords[final_url]
        if rating == 1:
            for keyword in update_keywords:
                if keyword in ranks:
                    ranks[keyword] += 1
                else:
                    print(':(')
        elif rating == 2:
            for keyword in update_keywords:
                if keyword in ranks:
                    ranks[keyword] -= 1
                else:
                  print(':)')

        ### Delete URL/destination
        urls.remove(choice1_url)
        url_to_keywords.pop(choice1_url)
        for biz in businesses:
            if biz["url"] == choice1_url:
                businesses.remove(biz)
        urls.remove(choice2_url)
        url_to_keywords.pop(choice2_url)
        for biz in businesses:
            if biz["url"] == choice2_url:
                businesses.remove(biz)

        max_keyword = max(ranks, key = lambda word: ranks[word])
        choice1_url = ""
        choice2_url = ""
        for url in url_to_keywords:
            if max_keyword in url_to_keywords[url]:
                choice1_url = url
                for biz in businesses:
                    if biz["url"] == choice1_url:
                        choice1 = businesses.index(biz)
                        break
                break
          
        choice2 = random.randrange(0, 10)
        choice2_url = urls[choice2]
        while choice1_url == choice2_url:
            choice2 = random.randrange(0, 10)
            choice2_url = urls[choice2]
    except:
      print("Thank you for using Milestones :)")
      keep_playing = False
