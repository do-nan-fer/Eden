import requests
from celery import shared_task 
#from .models import Plant
from datetime import datetime
import uuid

@shared_task(name='process_plants_with_status_1')
def process_plants_with_status_1():
    from .models import Plant
    beat_id = uuid.uuid4()  # Generate a unique beat ID for this execution
    execution_time = datetime.now().isoformat()  # Mark the start of the task execution

    responses = []  # Initialize an empty list to hold the API responses

    # Filter plants by collect=1
    plants = Plant.objects.filter(collect=1)
    for plant in plants:
        # Prepare parameters for the API call
        params = {plant.api_param_name: plant.api_param_value, 'key': plant.api_auth_key}
        
        # Make the API call
        response = requests.get(plant.api_endpoint, params=params)

        # Check the response status
        if response.status_code == 200:
            # If the call is successful, parse the response and add to the responses list
            api_response = response.json()
            responses.append(api_response)

            # Update the plant status to 1 (successful)
            plant.status = 1
        else:
            # If the call fails, update the plant status to 0 (failed)
            plant.status = 0

        # Save the plant object to update its status in the database
        plant.save()

    # After processing all plants, create a single document with all responses
    if responses:
        document = {
            "beat": str(beat_id),  # Use the generated beat ID
            "timestamp": execution_time,  # Use the task execution timestamp
            "responses": responses  # Include all collected API responses
        }

        # Define the OpenSearch URL and headers for the indexing request
        opensearch_url = 'https://192.168.101.11:9200/garden-plants/_doc'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic YWRtaW46YWRtaW4='  # Use the appropriate auth header
        }

        # Send the aggregated document to OpenSearch
        opensearch_response = requests.post(opensearch_url, json=document, headers=headers, verify=False)

        # Check the response status from OpenSearch
        if opensearch_response.status_code == 201:
            print(f"Aggregated document indexed successfully with Beat ID {beat_id}")
        else:
            print(f"Error indexing aggregated document: {opensearch_response.text}")

