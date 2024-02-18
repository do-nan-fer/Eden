import subprocess
from celery import shared_task
from datetime import datetime
import uuid
import requests
import json

@shared_task
def update_plant_status(plant_id):
    from .models import Plant
    try:
        plant = Plant.objects.get(id=plant_id)
        output = subprocess.run(plant.full_query_command, shell=True, capture_output=True, text=True)
        plant.status = 1 if output.returncode == 0 else 0
        plant.save()
    except Plant.DoesNotExist:
        print(f"Plant with id {plant_id} does not exist.")
    except Exception as e:
        print(f"Error executing command for plant {plant_id}: {e}")

@shared_task(name='process_plants_with_status_1')
def process_plants_with_status_1():
    from .models import Plant
    beat_id = str(uuid.uuid4())
    execution_time = datetime.now().isoformat()

    plants = Plant.objects.filter(collect=1, status=1)  # Active plants
    responses = []

    for plant in plants:
        try:
            output = subprocess.run(plant.full_query_command, shell=True, capture_output=True, text=True, check=True)
            api_response = json.loads(output.stdout.strip())  # Parse the API response as JSON

            # Append a dictionary to the responses list
            responses.append({"plant_id": str(plant.id), "plant_name": plant.name, "response": api_response})

        except subprocess.CalledProcessError as e:
            print(f"Command failed for plant {plant.name}: {e.stderr}")
        except Exception as e:
            print(f"Failed to fetch data for plant {plant.name} due to an error: {e}")

    # Ensure the entire document is valid JSON
    document = json.dumps({"beat": beat_id, "timestamp": execution_time, "responses": responses})

    if responses:
        opensearch_url = 'https://192.168.101.11:9200/garden-plants/_doc'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic YWRtaW46YWRtaW4='}
        upload_response = requests.post(opensearch_url, data=document, headers=headers, verify=False)

        if upload_response.status_code not in [200, 201]:
            print(f"Failed to upload document: {upload_response.text}")
        else:
            print("Successfully uploaded aggregated document to OpenSearch")

@shared_task(name='process_packages_with_latest_response')
def process_packages_with_latest_response():
    from .models import Package, Pick  # Importing models inside the task to avoid circular imports

    # Fetch the latest response from Elasticsearch
    response = requests.get(
        'https://192.168.101.11:9200/garden-plants/_search',
        auth=('admin', 'admin'),
        headers={'Content-Type': 'application/json'},
        json={
            "size": 1,
            "sort": [{"timestamp": {"order": "desc"}}],
            "query": {"match_all": {}}
        },
        verify=False
    )

    if response.status_code == 200 and response.json()['hits']['hits']:
        latest_document = response.json()['hits']['hits'][0]['_source']
        latest_response_data = latest_document['responses'][0]
        beat_id = latest_document['beat']

        packages_list = []

        # Iterate through all packages
        for package in Package.objects.all():
            picks_list = []
            
            # Access picks by their IDs stored in the package
            for pick_id in package.picks.values_list('id', flat=True):
                pick = Pick.objects.get(id=pick_id)
                api_fields_list = []

                # For each api_field in the pick, check if it exists in the latest response
                for api_field in pick.api_fields.all():
                    field_name_parts = api_field.name.split('.')
                    field_value = latest_response_data
                    for part in field_name_parts:
                        if part in field_value:
                            field_value = field_value[part]
                        else:
                            field_value = None
                            break

                    if field_value is not None:
                        api_fields_list.append({api_field.name: field_value})

                if api_fields_list:
                    picks_list.append({
                        "pick_id": pick_id,
                        "api_fields": api_fields_list
                    })

            if picks_list:
                packages_list.append({
                    "package_id": package.id,
                    "package_name": package.name,
                    "picks": picks_list
                })

        document = {
            "beat": beat_id,
            "timestamp": datetime.now().isoformat(),
            "packages": packages_list
        }

        # Define the URL for the garden-packages index
        opensearch_url = 'https://192.168.101.11:9200/garden-packages/_doc'

        # Send the document to the garden-packages index in Elasticsearch
        opensearch_response = requests.post(
            opensearch_url,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'},
            json=document,
            verify=False
        )

        # Check the response status from Elasticsearch
        if opensearch_response.status_code in [200, 201]:
            print(f"Document saved successfully in garden-packages with Beat ID {beat_id}")
        else:
            print(f"Error saving document in garden-packages: {opensearch_response.text}")

    else:
        print("Error fetching the latest response or no data available.")

