import time, json
import datetime
from scraper import Scraper, Studio
from flask import Flask, request

app = Flask(__name__)

@app.route('/time')
def get_current_time():
    return {'time': time.time()}


@app.route('/schedule')
def get_booking_schedule():
    scraper = None

    phone = request.args.get("phone")
    pwd = request.args.get("pwd")

    f = open("schedule.json", "r")

    cached_schedule = f.read()
    schedule = json.loads(cached_schedule)
    f.close()

    if len(schedule.items()) < 7:
        f = open("schedule.json", "w")
        scraper = Scraper(password=pwd, phone=phone, studio=Studio.MOHOLT)
        schedule = scraper.get_schedule()
        f.write(json.dumps(schedule))
        f.close()

    #TODO: fix /21 hardcoding
    dates = [datetime.datetime.strptime(k + '/21', '%d/%m/%y') for (k, v) in schedule.items()]

    # if less than 2 weeks is cached, scrape
    if dates[-1].isocalendar()[1] < 2 + datetime.date.today().isocalendar()[1]:
        print('CACHE OUTDATED...')
        print('INIT SCRAPING')
        scraper = Scraper(password=pwd, phone=phone, studio=Studio.MOHOLT)
        schedule = scraper.get_schedule()
        f = open("schedule.json", "w")
        f.write(json.dumps(schedule))
        f.close()
        print('SCRAPING SCHEDULE COMPLETE')
    else:
        print('USE CACHED SCHEDULE')

    if scraper is None:
        scraper = Scraper(password=pwd, phone=phone, studio=Studio.MOHOLT)
    print('FETCHING BOOKINGS')
    bookings = scraper.get_bookings()
    print('MERGE BOOKINGS')
    schedule = add_bookings(bookings, schedule)

    cached_schedule = json.dumps(schedule)
    print('COMPLETED')
    scraper.close_driver()

    return {
        'time': time.time(),
        'schedule': cached_schedule
    }

@app.route('/book', methods=['POST'])
def book_trainings():
    print(request.method)
    phone = request.args.get("phone")
    pwd = request.args.get("pwd")

    if len(set(request.json)) == 0:
        f = open("schedule.json", "r")
        schedule = json.loads(f.read())
        return app.response_class(status=200, response=json.dumps(schedule), mimetype='application/json')

    scraper = Scraper(password=pwd, phone=phone, studio=Studio.MOHOLT)

    bookings = {}
    for booking_id in set(request.json):
        bookings[booking_id] = scraper.book(booking_id)
        print(f'{booking_id} BOOKED')

    f = open("schedule.json", "r")
    schedule = json.loads(f.read())
    bookings = scraper.get_bookings()
    f.close()

    f = open("schedule.json", "w")
    f.write(json.dumps(schedule))
    f.close()

    schedule = add_bookings(bookings, schedule)
    scraper.close_driver()
    return app.response_class(status=200, response=json.dumps(schedule), mimetype='application/json')


def add_bookings(bookings, schedule):
    print(bookings)
    for booking in bookings:
        print(booking)
        datestamp = f'{booking["day"]}/{booking["month"]}'
        schedule[datestamp][booking['start']]['status'] = 'BOOKED'
    return schedule