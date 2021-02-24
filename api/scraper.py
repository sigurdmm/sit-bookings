from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import datetime


def parse_date(date_str):
    return date_str[-5:]


def parse_info(info_string, studio):
    info = info_string.split(',')
    return {
        'id': info[0].split('(')[1],
        'start': info[2].strip(" ").strip("'"),
        'end': info[3].strip(" ").strip("'"),
        'status': get_status(info_string),
        'studio': studio
    }


def get_status(info_string):
    info_tokens = info_string.split(',')
    status_icon = info_tokens[5]
    status_msg = info_tokens[6]

    # if status_msg.find('Du har plass på timen') != -1:
    #     return "BOOKED"
    if status_icon.find('locked') != -1:
        return "FUTURE"
    elif status_icon.find('check_wait') != -1:
        return "ONWAITINGLIST"
    elif status_msg.find('Reserver timen') != -1:
        return "BOOKABLE"
    elif status_msg.find('Sett på venteliste') != -1:
        return "WAITINGLIST"
    elif status_msg.find('fullbooket') != -1:
        return "FULL"
    return "UNKNOWN"


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    # avoids the popup of a chrome window
    options.add_argument('headless')
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)


class Studio:
    GLOSHAUGEN = 306
    DRAGVOLL = 307
    PORTALEN = 308
    DMMH = 402
    MOHOLT = 540


class Scraper:

    def __init__(self, phone, password, studio=Studio.MOHOLT):
        self.phone = phone
        self.studio = studio
        self.driver = get_driver()
        self.login(password)

    def close_driver(self):
        self.driver.close()

    def get_schedule(self):
        return self.scrape_schedule()

    def login(self, password):
        self.driver.get(f'https://ibooking.sit.no/index.php?location={self.studio}&type=13&week=now')

        login_button = self.driver.find_element_by_css_selector('body > div.booking-selects > div.menu > a:nth-child(1)')
        login_button.click()

        self.driver.find_element_by_css_selector('#username').send_keys(self.phone)
        self.driver.find_element_by_css_selector('#password').send_keys(password)

        self.driver.find_element_by_css_selector('#forms > form > input.btn.btn-primary.submit').click()


    def scrape_schedule(self):
        self.driver.get(f'https://ibooking.sit.no/index.php?location={self.studio}&type=13&week=now')
        this_week = self.scrape_week()
        self.driver.get(f'https://ibooking.sit.no/index.php?location={self.studio}&type=13&week=%2B1+weeks')
        next_week = self.scrape_week()
        self.driver.get(f'https://ibooking.sit.no/index.php?location={self.studio}&type=13&week=%2B2+weeks')
        nextnext_week = self.scrape_week()
        return {**this_week, **next_week, **nextnext_week}

    def scrape_week(self):
        week = {}

        available_dates = self.driver.find_elements_by_css_selector('#schedule > ul:not(.dimmed)')

        for date in available_dates:
            date_string = parse_date(date.find_element_by_class_name('header').text)
            this_year = datetime.date.today().year
            current_date = datetime.date(this_year, int(date_string[-2:]), int(date_string[:2]))

            #don't scrape previous days
            if current_date < datetime.date.today():
                continue

            week[date_string] = {}

            time_elements = date.find_elements_by_css_selector('li[data-type-id="13"] > div')
            for time in time_elements:
                time_info = parse_info(time.get_attribute('onclick'), self.studio)

                hour = int(time_info['start'].split(':')[0])
                minutes = int(time_info['start'].split(':')[1])
                timestamp = datetime.datetime(this_year, int(date_string[-2:]), int(date_string[:2]), hour, minutes)
                #dont store time_elements on current day, but before time of scraping
                if timestamp < datetime.datetime.now():
                    continue
                week[date_string][time_info['start']] = time_info
        return week

    def get_bookings(self):
        self.driver.get(f'https://ibooking.sit.no/minside/?action=reservations')
        reservations_table = self.driver.find_elements_by_css_selector('#myPageContent > table')[0]
        reservation_elements = reservations_table.find_elements_by_css_selector('tbody > tr > td:nth-child(3)')

        bookings = []

        for i in reservation_elements:

            norwegian_months = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september',
                                'oktober', 'november', 'desember']
            date_array = i.text.split(' ')

            # 3 => 03, 14 => 14
            day_str = date_array[0].strip('.')
            if len(day_str) == 1:
                day_str = f'0{day_str}'

            # 2 => 02, 12 => 12
            print(day_str)
            if "".join(date_array).lower().find('morgen') != -1:
                day_str = (datetime.date.today() + datetime.timedelta(days=1)).day
                month_str = (datetime.date.today() + datetime.timedelta(days=1)).month
            elif "".join(date_array).lower().find('dag') != -1:
                day_str = datetime.date.today().day
                month_str = datetime.date.today().month
            else:
                month_str = norwegian_months.index(date_array[1].lower())+1

            if int(month_str) < 10:
                month_str = f'0{month_str}'

            # 9:00 => 09:00, 17:00 => 17:00
            time_str = date_array[3]
            if len(time_str) == 4:
                time_str = f'0{time_str}'

            if time_str.split(':')[1] == '00':
                bookings.append({
                    'day': day_str,
                    'month': month_str,
                    'start': time_str
                })
        return bookings


    def book(self, id):
        self.driver.get(f'https://ibooking.sit.no/index.php?page=reservation&aid={id}')
        self.driver.find_element_by_css_selector('#reservation > form > input.btn.btn-success').click()
        response = self.driver.find_element_by_css_selector('#forms > div.messageText').text
        if response.find("Reservasjon fullført") != -1:
            return True
        return False
