from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import sys
from create_db import *
import slack 

browser = webdriver.Chrome(executable_path="C:/Users/Tam Nguyen/Downloads/chromedriver_win32/chromedriver.exe")


def chooseTicketType():
    ticket_type = browser.find_element_by_css_selector("label#flight-type-roundtrip-label-hp-flight")
    ticket_type.click()

def chooseOrigin(departure_country):
    flying_from = browser.find_element_by_css_selector('input#flight-origin-hp-flight')
    flying_from.clear()
    time.sleep(2)
    flying_from.send_keys(departure_country)
    time.sleep(2)
    item = browser.find_element_by_css_selector('a#aria-option-0')
    item.click()

def chooseDestination(destination):
    flying_to = browser.find_element_by_css_selector('input#flight-destination-hp-flight')
    flying_to.clear()
    time.sleep(2)
    flying_to.send_keys(destination)
    time.sleep(2)
    item = browser.find_element_by_css_selector('a#aria-option-0')
    item.click()

def chooseDepartureDate(month, day, year):
    date = browser.find_element_by_css_selector('input#flight-departing-hp-flight')
    date.clear()
    date.send_keys(month + '/' + day + '/' + year)

def chooseReturnDate(month, day, year): 
    date = browser.find_element_by_css_selector('input#flight-returning-hp-flight')
    for i in range(11):
        date.send_keys(Keys.BACKSPACE)
    date.send_keys(month + '/' + day + '/' + year)

def search():
    search_btn = browser.find_element_by_css_selector('button.btn-primary.btn-action.gcw-submit')
    search_btn.click()
    time.sleep(15)
    print('Done!')

def extract_data(conn): 
    airline = browser.find_elements_by_xpath("//span[@data-test-id='airline-name']")
    airline_list = [element.text for element in airline]

    price = browser.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    price_list = [element.text for element in price]

    duration = browser.find_elements_by_xpath("//span[@data-test-id='duration']")
    duration_list = [element.text for element in duration]

    stop = browser.find_elements_by_xpath("//span[@class='number-stops']")
    stop_list = [element.text for element in stop]

    departure_time = browser.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    departure_time_list = [time.text for time in departure_time]

    arrival_time = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arrival_time_list = [time.text for time in arrival_time]

    flight_route = browser.find_elements_by_xpath("//div[@data-test-id='flight-info']")
    flight_route_list = [info.text for info in flight_route]

    for i in range(len(airline_list)):
        with conn: 
            flight = (airline_list[i], price_list[i], duration_list[i], stop_list[i], departure_time_list[i], arrival_time_list[i], flight_route_list[i])
            insert_flight(conn, flight)

def post_to_slack(message):
    sc = slack.WebClient(token)
    sc.api_call(
        "chat.postMessage", json={'channel':'#flight-bot', 'text':message,
        'username':'flight_search_bot', 'icon_emoji':':robot_face:'})

def get_cheapest_ticket(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM flights ORDER BY price ASC LIMIT 1")
    row = cur.fetchall()
    print(row)
    return row

def main(): 
    conn = create_connection('flight_data.db')
    while True:
        try:  
            link = 'https://www.expedia.com/'
            browser.get(link)
            time.sleep(5)

            #choose flights only
            flights_only = browser.find_element_by_xpath("//button[@id='tab-flight-tab-hp']")
            flights_only.click()

            chooseTicketType()
            chooseOrigin('New York')
            chooseDestination('Hanoi')
            chooseDepartureDate('12', '21', '2019')
            chooseReturnDate('01', '19', '2020')
            search()

            extract_data(conn)
            with conn: 
                message = get_cheapest_ticket(conn)[0]
            post_to_slack(message)

            time.sleep(3600)
            
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)

if __name__ == "__main__":
    main()
