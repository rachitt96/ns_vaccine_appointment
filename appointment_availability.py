import requests
from datetime import datetime
from datetime import timedelta
from datetime import date
import pytz

def get_available_vaccine_appointments(location_filter = True, get_time_slots = True, interested_vaccines = ["pfizer", "moderna", "astrazeneca"], print_in_console = True, interested_locations = None):
    """
    A function to print all clinic (with available time slots) in interested cities where appointment is available. Respose is based on real time.

    Arguments:
        location_filter: (bool) True if want to filter availability through clinic's address (city name, or street name, or postal code), False otherwise
        get_time_slots: (bool) True if want to print availble time slots with dates, False if don't want to print date and time
        interested_locations: (list) list of substrings that we want me match with clinic's address (required only if location_filter is set to True)

    Returns:
        None. This function just prints clinic details where the appointment is available
    """

    all_clinics_details_url = "https://sync-cf2-1.canimmunize.ca/fhir/v1/public/booking-page/17430812-2095-4a35-a523-bb5ce45d60f1/appointment-types"
    clinic_timeslots_url = "https://sync-cf2-1.canimmunize.ca/fhir/v1/public/availability/17430812-2095-4a35-a523-bb5ce45d60f1"

    all_clinics_resonse = requests.get(
        all_clinics_details_url,
        params = {
            'forceUseCurrentAppointment': False,
            'preview': False
        }
    )

    all_clinics_response_json = all_clinics_resonse.json()

    result_json_dict_template = {
        'clinic_address': '',
        'clinic_name': '',
        'vaccine': '',
        'available_date_time': {
            'date': [],
            'time_slots': []
        }
    }
    filtered_results = [result_json_dict_template]
    appointment_found_count = -1

    for index, each_clinic in enumerate(all_clinics_response_json['results']):
        if(each_clinic["status"] == "active" and each_clinic["fullyBooked"] == False):
            if location_filter:
                clinic_address = each_clinic["mapsLocationString"].lower()
                location_matched = any([x in clinic_address for x in interested_locations])

                if not location_matched:
                    continue

            clinic_name = each_clinic["nameEn"].lower()
            vaccine_name_matched = any([x in clinic_name for x in interested_vaccines])

            if not vaccine_name_matched:
                continue
            
            print("***************** appointment found **************")
            print()
            print(each_clinic["mapsLocationString"])
            print("Age Eligibility: " + str(each_clinic["minAge"]) + "+")
            #print("Vaccine: " + each_clinic["clinicName"].split(" ")[-1])
            print("Vaccine: " + each_clinic["nameEn"].split(" ")[-1])

            appointment_found_count += 1

            filtered_results[appointment_found_count]['clinic_address'] = each_clinic["mapsLocationString"]
            filtered_results[appointment_found_count]['clinic_name'] = each_clinic["clinicName"]
            filtered_results[appointment_found_count]['vaccine'] = each_clinic["nameEn"].split(" ")[-1]

            if(get_time_slots):
                current_date = date.today()
                end_date = current_date + timedelta(days=30)

                clinic_available_time_slots_response = requests.get(
                    clinic_timeslots_url,
                    params = {
                        'appointmentTypeId': each_clinic["appointmentTypeId"],
                        'timezone': "America/Halifax",
                        'startDate': current_date.strftime('%Y-%m-%d'),
                        'preview': False
                    }
                )

                clinic_available_time_slots_response_json = clinic_available_time_slots_response.json()
                clinic_available_time_slots_response_json_list = []

                while len(clinic_available_time_slots_response_json) > 0:
                    clinic_available_time_slots_response_json_list.append(clinic_available_time_slots_response_json[0])
                    clinic_available_time_slots_response = requests.get(
                        clinic_timeslots_url,
                        params = {
                            'appointmentTypeId': each_clinic["appointmentTypeId"],
                            'timezone': "America/Halifax",
                            'startDate': (datetime.strptime(clinic_available_time_slots_response_json[0]["date"], "%Y-%m-%d") + timedelta(days=1)).strftime('%Y-%m-%d'),
                            'preview': False
                        }
                    )
                    clinic_available_time_slots_response_json = clinic_available_time_slots_response.json()

                
                for available_day_json in clinic_available_time_slots_response_json_list:
                    print("\t" + available_day_json["date"])
                    print('\t' + str([pytz.utc.localize(datetime.strptime(each_time_slot["time"], "%Y-%m-%dT%H:%M:%S.%fZ")).astimezone(pytz.timezone("America/Halifax")).time().strftime("%H:%M") for each_time_slot in available_day_json["availabilities"]]))
                    print()

                    filtered_results[appointment_found_count]['available_date_time']['date'].append(available_day_json["date"])
                    filtered_results[appointment_found_count]['available_date_time']['time_slots'].append([pytz.utc.localize(datetime.strptime(each_time_slot["time"], "%Y-%m-%dT%H:%M:%S.%fZ")).astimezone(pytz.timezone("America/Halifax")).time().strftime("%H:%M") for each_time_slot in available_day_json["availabilities"]])            
            
            filtered_results.append(result_json_dict_template)
            print()

    filtered_results_new = list(filter(lambda d: len(d['available_date_time']['date']) > 0, filtered_results))
    return filtered_results_new

if(__name__ == "__main__"):

    interested_locations = ["halifax", "bedford"]
    location_filter = True
    get_time_slots = True
    interested_vaccines = ["pfizer"]
    
    get_available_vaccine_appointments(
        location_filter = location_filter,
        get_time_slots = get_time_slots,
        interested_locations = interested_locations,
        interested_vaccines = interested_vaccines
    )