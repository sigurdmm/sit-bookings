import time, json
import datetime
from scraper import Scraper, Studio
import googlecalendar
from flask import Flask, request

app = Flask(__name__)


@app.route('/api/schedule')
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

    # TODO: fix /21 hardcoding
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
    update_calendar(schedule)
    print('CALENDAR UPDATE COMPLETED')
    cached_schedule = json.dumps(schedule)
    print('COMPLETED')
    scraper.close_driver()

    return {
        'time': time.time(),
        'schedule': cached_schedule
    }


@app.route('/api/book', methods=['POST'])
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
    update_calendar(schedule)
    scraper.close_driver()
    return app.response_class(status=200, response=json.dumps(schedule), mimetype='application/json')


def add_bookings(bookings, schedule):
    for booking in bookings:
        datestamp = f'{booking["day"]}/{booking["month"]}'
        schedule[datestamp][booking['start']]['status'] = 'BOOKED'
    return schedule


def update_calendar(schedule):
    calender = googlecalendar.Calendar()
    calender_events = [event for event in calender.get_events()]

    booked_activities = []
    for date in schedule:
        for time in schedule[date]:
            if schedule[date][time]['status'] == 'BOOKED':
                booked_activities.append({**schedule[date][time], **{'date': date}})

    add_calender_events(calender, booked_activities, calender_events)
    delete_removed_events(calender, booked_activities, calender_events)


def add_calender_events(calender, booked_activities, calender_events):
    event_descriptions = [event['description'] for event in calender_events if 'description' in event]

    for booking in booked_activities:
        # Dont make calendar event for bookings already in calendar
        if booking['id'] in event_descriptions:
            continue

        calendar_event = {
            'start': get_datetime(booking['date'], booking['start']).isoformat(),
            'end': get_datetime(booking['date'], booking['end']).isoformat(),
            'description': booking['id'],
            'summary': 'TPM BOOKING',
        }
        calender.create_event(calendar_event)
        print(f'ADDED:{booking["date"]}-{booking["start"]} - ID{booking["id"]}')


def delete_removed_events(calendar, booked_activities, calendar_events):
    booked_activity_ids = set([activity['id'] for activity in booked_activities])
    # contains the calendar event id for activities which is in the calendar, but is not booked anymore.
    deleted_activity_calendar_ids = []
    for event in calendar_events:
        if 'description' in event and event['description'] not in booked_activity_ids:
            deleted_activity_calendar_ids.append(event['id'])

    for eventID in deleted_activity_calendar_ids:
        calendar.delete_event(eventID)
        print('deleted, ', eventID)


def get_datetime(datestr, timestr):
    year = 2021
    month = int(datestr.split('/')[1])
    day = int(datestr.split('/')[0])
    hour = int(timestr.split(':')[0])
    minutes = int(timestr.split(':')[1])
    return datetime.datetime(year, month, day, hour, minutes)
