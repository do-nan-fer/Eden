import subprocess
from celery import shared_task
from datetime import datetime, timezone
import uuid
import requests
import json

@shared_task
def update_plant_status(plant_id):
    from .models import Plant
    try:
        plant = Plant.objects.get(id=plant_id)
        output = subprocess.run(plant.full_query_command, shell=True, capture_output=True, text=True)
        new_status = 1 if output.returncode == 0 else 0

        if plant.status != new_status:
            plant.status = new_status
            plant.last_status_change = timezone.now()
            plant.save()

    except Plant.DoesNotExist:
        print(f"Plant with id {plant_id} does not exist.")
    except Exception as e:
        print(f"Error executing command for plant {plant_id}: {e}")

@shared_task(name='process_packages_with_latest_response')
def process_packages_with_latest_response():
    from .models import Package, Pick
    response = requests.get(
        'https://192.168.101.11:9200/garden-plants/_search',
        auth=('admin', 'admin'),  # Replace with actual credentials
        headers={'Content-Type': 'application/json'},
        json={
            "size": 1,
            "sort": [{"timestamp": {"order": "desc"}}],
            "query": {"match_all": {}}
        },
        verify=False  # Note: Address SSL certificate verification
    )

    if response.status_code == 200 and response.json()['hits']['hits']:
        latest_document = response.json()['hits']['hits'][0]['_source']
        latest_response_data = latest_document['responses']
        beat_id = latest_document['beat']

        print("Latest Response Data:")
        print(latest_response_data)

        packages_list = []

        for package in Package.objects.all():
            picks_list = []

            for pick in package.picks.all():
                plant = pick.plant  # Fetch the Plant associated with this Pick

                api_fields_list = []

                for api_field in pick.api_fields.all():
                    field_value = None

                    for data in latest_response_data:
                        response_data = data.get('response', {})
                        for key, value in response_data.items():
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    if api_field.name == f"{key}.{sub_key}":
                                        field_value = sub_value
                                        break
                            elif api_field.name == key:
                                field_value = value
                                break

                    if field_value is not None and field_value != []:
                        api_fields_list.append({api_field.name: field_value})

                if api_fields_list:
                    pick_data = {
                        "pick_id": pick.id,
                        "plant_id": plant.id,
                        "plant_name": plant.name,
                        "api_fields": api_fields_list
                    }
                    picks_list.append(pick_data)

            if picks_list:
                package_data = {
                    "package_id": package.id,
                    "package_name": package.name,
                    "picks": picks_list
                }
                packages_list.append(package_data)

        document = {
            "beat": beat_id,
            "timestamp": datetime.now().isoformat(),
            "packages": packages_list
        }

        opensearch_response = requests.post(
            'https://192.168.101.11:9200/garden-packages/_doc',
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'},
            json=document,
            verify=False
        )

        if opensearch_response.status_code in [200, 201]:
            print(f"Document saved successfully in garden-packages with Beat ID {beat_id}")
        else:
            print(f"Error saving document in garden-packages: {opensearch_response.text}")

    else:
        print("Error fetching the latest response or no data available.")
