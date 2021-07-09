import os
import json

from google.auth import jwt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.cloud import pubsub_v1
from dotenv import load_dotenv
import google.auth

from appointment_availability import get_available_vaccine_appointments

load_dotenv()

def generate_email(available_appointments_list):

    html_content = ""

    for index, appointment in enumerate(available_appointments_list):
        html_content += ("<h3> Appointment #: " + str(index) + "</h3>"
        "<div>" + "<b>Clinic Name: </b>" + appointment['clinic_name'] + "<br>"
        "<b>Clinic Address: </b>" + appointment['clinic_address'] + "<br>"
        "<b>Vaccine Name: </b>" + appointment['vaccine'] + "<br></div>")

        for date_index, available_day in enumerate(appointment['available_date_time']['date']):
            html_content += ("<div style='margin-left: 40px'><b> Date: </b>" + available_day + "<br>"
            "<b> Time: </b>" + str(appointment['available_date_time']['time_slots'][date_index]) + "<br>"
            "<br></div>")

    message = Mail(
        from_email='zmahbouldztbc@gmailni.com',
        to_emails='rachitt96@gmail.com',
        subject='Automatic appointment notification',
        html_content=html_content)
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.message)
    

topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    topic=os.getenv('GOOGLE_CLOUD_PUBSUB_TOPIC_NAME'),  # Set this to something appropriate.
)

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    sub=os.getenv('GOOGLE_CLOUD_PUBSUB_SUBSCRIPTION_NAME'),  # Set this to something appropriate.
)

'''
service_account_info = json.load(open("ns-vaccination-availability-f57e42ad5b68.json"))

credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience="https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"
)
'''

credentials, project = google.auth.default()

def callback(message):

    interested_locations = ["halifax", "bedford", "dartmouth"]
    location_filter = True
    get_time_slots = True
    interested_vaccines = ["pfizer"]

    filtered_appointments = get_available_vaccine_appointments(
        location_filter = location_filter,
        get_time_slots = get_time_slots,
        interested_locations = interested_locations,
        interested_vaccines = interested_vaccines
    )

    if(len(filtered_appointments) > 0):
        generate_email(
            available_appointments_list = filtered_appointments
        )

    message.ack()

with pubsub_v1.SubscriberClient(credentials=credentials) as subscriber:
    future = subscriber.subscribe(subscription_name, callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()