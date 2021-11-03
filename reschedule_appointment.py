import requests
from datetime import datetime, time
import json
import sys
from dotenv import load_dotenv
import os

load_dotenv()

def automatically_reschedule_appointment(available_appointments_list, time_threshold_str):

    time_threshold = datetime.strptime(time_threshold_str, "%H:%M").time()
    appointment_id = os.getenv('CANIMUNIZE_APPOINTMENT_ID') # this appointment id is unique for each peron. After rescheduling the appointment too, this id will stay same, but only details associated with it will change.
    #print(available_appointments_list)
    
    for index, appointment in enumerate(available_appointments_list):
        time_index_matched = -1
        date_index_matched = -1
        for date_index, available_day in enumerate(appointment['available_date_time']['date']):
            #date_index_matched = date_index
            if(time_index_matched > -1):
                break
            for time_index, available_time_str in enumerate(appointment['available_date_time']['time_slots'][date_index]):
                available_time = datetime.strptime(available_time_str, "%H:%M").time()
                if(available_time >= time_threshold):
                    date_index_matched = date_index
                    time_index_matched = time_index
                    break

        if(time_index_matched > -1):
            print("************ appointment booked **************")
            print(appointment['clinic_reschedule_details'])

            selected_target_json = appointment['clinic_reschedule_details']

            print(date_index_matched)
            print(time_index_matched)

            selected_original_datetime = appointment['clinic_reschedule_details']['datetime'][date_index_matched][time_index_matched]
            selected_target_json['datetime'] = selected_original_datetime

            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            data = {
                'target': selected_target_json,
                'waitlist': False
            }

            data_json = json.dumps(data)
            print(data_json)

            r = requests.post(
                'https://sync-cf2-1.canimmunize.ca/fhir/v1/public/appointment/{appointment_id}/reschedule'.format(appointment_id=appointment_id),
                data = json.dumps(data),
                headers = headers
            )

            print(r)
            sys.exit(0)