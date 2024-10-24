from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Scroll to the bottom of the page to ensure all content is loaded
def scroll_to_bottom(driver, pause_time=3):
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get initial page height
    
    while True:
        # Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)  # Wait for the page to load
        
        # Check the new page height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If the page height hasn't changed, assume that all content is loaded
            break
        last_height = new_height

# Extract user ID from a URL
def extract_user_id(url):
    return url.rstrip('/').split('/')[-1]

# Extract event links from the given URL
def extract_event_links(driver, url):
    driver.get(url)
    driver.implicitly_wait(5)

    events = []

    # Scroll the page to ensure all content is fully loaded
    scroll_to_bottom(driver)
    
    # Find all <a> tags that have the aria-label and href attributes
    try:
        event_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'timeline')]"))
        )
        event_links = event_section.find_elements(By.XPATH, "//a[@aria-label and @href and contains(@class, 'event-link content-link')]")
    except Exception as e:
        print(f"Could not find matching <a> tags: {e}")
        return []

    # Iterate through each <a> tag to extract aria-label and href attributes
    for link in event_links:
        event = {}
        try:
            event["aria-label"] = link.get_attribute("aria-label")
            event["href"] = link.get_attribute("href")
            event["source"] = "luma"
            events.append(event)
        except Exception as e:
            print(f"Error extracting aria-label or href: {e}")
            event["aria-label"] = "N/A"
            event["href"] = "N/A"

    return events

# Extract detailed event information from the given URL
def extract_event_info(driver, url):
    driver.get(url)
    driver.implicitly_wait(5)

    event_info = {}

    try:
        # Get the calendar information from the event page
        calendar_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, './/div[contains(@class, "event-page-left")]'))
        )

        try:
            calendar = calendar_div.find_element(By.XPATH, './/div[2]/div/div/div/div/div/a[1]')
        except Exception as e:
            print(f"Could not find calendar: {e}")
            calendar = None

        if calendar:
            try:
                name = calendar.find_element(By.XPATH, ".//div[1]/div[1]").text
            except Exception as e:
                print(f"Could not find name: {e}")
                name = ""

            try:
                link = calendar.get_attribute("href")
            except Exception as e:
                print(f"Could not find link: {e}")
                link = ""
        else:
            name = ""
            link = ""

        event_info['source_name'] = name
        event_info['source_link'] = link

        # Extract JSON-LD event information from the page
        json_ld_element = driver.find_element(By.XPATH, "//script[@type='application/ld+json']")
        json_ld_data = json.loads(json_ld_element.get_attribute("innerHTML"))

        event_info['event_name'] = json_ld_data.get("name", "N/A")
        event_info['start_date'] = json_ld_data.get("startDate", "N/A")
        event_info['end_date'] = json_ld_data.get("endDate", "N/A")
        event_info['location'] = json_ld_data.get("location", {}).get("name", "N/A")
        event_info['description'] = json_ld_data.get("description", "N/A")
        event_info['offers'] = [offer.get("name", "N/A") for offer in json_ld_data.get("offers", [])]
        event_info['organizers'] = [extract_user_id(org.get("name", "")) for org in json_ld_data.get("organizer", [])]
        event_info['performers'] = [extract_user_id(perf.get("name", "")) for perf in json_ld_data.get("performer", [])]
        event_info['status'] = extract_user_id(json_ld_data.get("eventStatus", ""))

    except Exception as e:
        print(f"Error extracting event information: {e}")
        event_info["error"] = str(e)

    return event_info
