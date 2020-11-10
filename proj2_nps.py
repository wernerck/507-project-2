#################################
##### Name: Christian Werner
##### Uniqname: wernerck
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

# Request header
headers = {
    'User-Agent': 'UMSI 507 Course Project - Python Scraping',
    'From': 'wernerck@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

# API from secrets file
api_key = secrets.API_KEY 

# CACHE
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    # Class constants to parse HTML
    SITE_CATEGORY_DIV_CLASS = 'Hero-designationContainer'
    SITE_CATEGORY_CONTAINER_TAG = 'span'
    NAME_DIV_CLASS = 'Hero-titleContainer clearfix'
    NAME_CONTAINER_TAG = 'a'
    NAME_CONTAINER_TAG_2 = 'span'
    ADDRESS_DIV_ITEMPROP = 'address'
    ADDRESS_CONTAINER_TAG = 'p'
    ADDRESS_CONTAINER_TAG_2 = 'span'
    PHONE_DIV_CLASS = 'vcard'
    PHONE_CONTAINER_TAG = 'p'
    PHONE_CONTAINER_TAG_2 = 'span'

    def __init__(self, url, details_soup):
        self.url = url
        self.category = self.extract_category(details_soup)
        self.name = self.extract_name(details_soup)
        self.address = self.extract_address(details_soup)
        self.zipcode = self.extract_zipcode(details_soup)
        self.phone = self.extract_phone(details_soup)

    def extract_category(self, soup):
        return(soup
            .find(class_=self.SITE_CATEGORY_DIV_CLASS)
            .find(self.SITE_CATEGORY_CONTAINER_TAG, class_='Hero-designation')
            .next_element
            .strip())

    def extract_name(self, soup):
        nm = soup.find(class_=self.NAME_DIV_CLASS).find(self.NAME_CONTAINER_TAG, class_='Hero-title -long')
        nm2 = soup.find(class_=self.NAME_DIV_CLASS).find(self.NAME_CONTAINER_TAG, class_='Hero-title')
        if nm != None:
            return nm.next_element.strip()
        elif nm == None:
            return nm2.next_element.strip()

    def extract_address(self, soup):
        try: # use try/catch because some parks are missing an address 
            adr_city = (soup.find(itemprop=self.ADDRESS_DIV_ITEMPROP)
            .find(self.ADDRESS_CONTAINER_TAG)
            .find(self.ADDRESS_CONTAINER_TAG_2, itemprop='addressLocality')
            .next_element
            .strip())
            adr_state = (soup.find(itemprop=self.ADDRESS_DIV_ITEMPROP)
            .find(self.ADDRESS_CONTAINER_TAG)
            .find(self.ADDRESS_CONTAINER_TAG_2, itemprop='addressRegion')
            .next_element
            .strip())
            return adr_city + ', ' + adr_state
        except:
            return "No address"

    def extract_zipcode(self, soup):
        try: # use try/catch because some parks are missing a zipcode
            zipc = (soup.find(itemprop=self.ADDRESS_DIV_ITEMPROP)
            .find(self.ADDRESS_CONTAINER_TAG)
            .find(self.ADDRESS_CONTAINER_TAG_2, itemprop='postalCode')
            .next_element
            .strip())
            return zipc
        except:
            return "No zipcode"

    def extract_phone(self, soup):
        try: # use try/catch because some parks are missing a phone number
            phn = (soup.
            find(class_=self.PHONE_DIV_CLASS)
            .find(self.PHONE_CONTAINER_TAG_2, class_="tel")
            .next_element
            .strip())
            return phn
        except:
            return "No phone number"
    
    def info(self): # info.self() to be displayed in interactive search
        return str(self.name) + " (" + str(self.category) + "): " + str(self.address) + " " +str(self.zipcode)


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    BASE_URL = 'https://www.nps.gov' 
    STATE_LIST_DIV_CLASS = 'SearchBar-keywordSearch input-group input-group-lg' # to parse state list

    states = {}
    state_page_url = BASE_URL

    response = requests.get(state_page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    state_list_parent = soup.find(class_=STATE_LIST_DIV_CLASS)
    state_list_ul = state_list_parent.find('ul', class_ ='dropdown-menu SearchBar-keywordSearch', recursive=False)

    for tag in state_list_ul.find_all('a'):
        state_link_tag = tag.next_element
        state_details_path = tag.get('href')
        state_details_url = BASE_URL + state_details_path 
        states[state_link_tag.lower()] = state_details_url
    return states 

### CACHING ###
def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    CACHE_FILE_NAME = 'cache.json'
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): 
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url, headers=headers)
        cache[url] = response.text 
        save_cache(cache)
        return cache[url] 

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response = requests.get(site_url, headers=headers) # include headers in the request
    url_text = make_url_request_using_cache(site_url, CACHE_DICT) # implement caching
    soup = BeautifulSoup(response.text, 'html.parser')
    return NationalSite(url_text, soup) # create an instance of a NationalSite

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    BASE_URL = 'https://www.nps.gov'
    PARK_LIST_DIV_CLASS = 'parkListResultsArea' # for parsing HTML
    
    site_page_url = state_url 
    response = requests.get(site_page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    park_parent_div = soup.find(id=PARK_LIST_DIV_CLASS)
    park_child_ul = park_parent_div.find('ul')

    state_site_urls = [] # create list of national site urls for one state
    for tag in park_child_ul.find_all('h3'):
        site_details_path = tag.find('a').get('href')
        site_details_url = BASE_URL + site_details_path # only need to add the national site extension to create functioning url
        state_site_urls.append(site_details_url)

    site_instances = [] # create instances of NationalSites from the urls
    for url in state_site_urls:
        site_instances.append(get_site_instance(url)) 
    return site_instances
    

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    load_cache()
    zipcode = site_object.zipcode # from zipcode determined in interactive portion
    mapquest_url = "http://www.mapquestapi.com/search/v2/radius"

    # create params dictionary
    params = {}
    params["key"] = api_key
    params["origin"] = zipcode
    params["maxMatches"] = 10
    params["ambiguities"] = "ignore"
    params["radius"] = 10
    params["units"] = "m"
    params["outFormat"] = "json"

    # construct unique key
    alphabetized_keys = sorted(params.keys())
    param_strings = []

    for k in alphabetized_keys:
        param_strings.append("{}-{}".format(k, params[k]))
    uniq_url = mapquest_url + "_" + "_".join(param_strings)

    if uniq_url in CACHE_DICT.keys():
        print("Using cache")
    else:
        print("Fetching")
        new_request = requests.get(mapquest_url, params=params)
        CACHE_DICT[uniq_url] = new_request.json()
        with open(CACHE_FILE_NAME, 'w') as outfile:
            outfile.write(json.dumps(CACHE_DICT, indent=2))
        outfile.close()
    return CACHE_DICT[uniq_url]

##########################
#########  MAIN ##########
##########################

if __name__ == "__main__":
    CACHE_DICT = load_cache()

    # states dict with states and state urls 
    state_dict = build_state_url_dict() 

    ##### Interactive #####
    flag = True # set flag
    while flag == True:
        flagstate = True
        while flagstate == True: 
            print()
            state_name = input("Enter a state or territory name (e.g. Michigan, michigan, Guam) or \"exit\": ").lower() 
            # force state_name to lower case
            # both states and territories are in the list

            if state_name == "exit":
                print()
                print("Goodbye!")
                break

            if state_name.lower() not in state_dict:
                print()
                print("Enter a proper state or territory name!")
            else: 
                break

        # get state url
        url = state_dict[state_name]
        site_instances = get_sites_for_state(url) # list of instances

        print('-' * 40)
        print("List of national sites in", state_name.capitalize()) # force all to capitalize for aesthetics 
        print('-' * 40)

        count = 1
        for site in site_instances:
            # national site output
            print("[" + str(count) + "] " + site.info())
            count += 1

        # Mapquest API
        flagchoice = True # set flag
        while flagchoice == True: 
            print()
            choice = input("Choose a number from the National Sites list for detailed search or \"exit\" or \"back\": ")

            if choice.isnumeric() == False: 
                if choice == "exit":
                    print()
                    print("Goodbye!")
                    break
                
                if choice == "back":
                    flagchoice = False # break out of the loop to go "back"
                    break

                else:
                    print()
                    print("[Error] You must choose a number or \"exit\" or \"back\"")

            if choice.isnumeric() == True: 
                if int(choice) >= count:
                    print()
                    print("[Error] Choose a number within the list range")

                else:
                    site_name = site_instances[int(choice)-1]
                    zipcode = site_name.zipcode
                    nearby_places = get_nearby_places(site_name)
                    print('-' * 40)
                    print("Places near", str(site_name.name)) # make sure this is the site that corresponds to the number 
                    print('-' * 40)

                    for p in range(len(nearby_places)):
                        name = nearby_places["searchResults"][p]["fields"]["name"]
                        category = nearby_places["searchResults"][p]["fields"]["group_sic_code_name_ext"]
                        street_address = nearby_places["searchResults"][p]["fields"]["address"]
                        city_name = nearby_places["searchResults"][p]["fields"]["city"]
                        
                        # default options if data are not available
                        if name == "":
                            name = "no name"
                        if category == "":
                            category = "no category"
                        if street_address == "":
                            street_address = "no street address"
                        if city_name == "":
                            city_name = "no city"

                        # nearby places output
                        print(" - " + str(name) + " (" + str(category) + "): " + str(street_address) + ", " + str(city_name))