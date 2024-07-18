import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import os
from urllib.parse import urlparse

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="overlayvideo", methods=["POST"])
def overlayvideo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid request body. Please provide a valid JSON.",
            status_code=400
        )

    blob_url = req_body.get('blob_url')
    content_tags = req_body.get('content_tags')
    
    if not blob_url:
        return func.HttpResponse(
            "Please provide a blob_url in the request body.",
            status_code=400
        )

    if not content_tags:
        return func.HttpResponse(
            "Please provide content_tags in the request body.",
            status_code=400
        )

    try:
        # Parse the blob URL to get the container name and blob name
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
        parsed_url = urlparse(blob_url)
        path_parts = parsed_url.path.lstrip('/').split('/')
        container_name = path_parts[0]
        blob_name = '/'.join(path_parts[1:])
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Download the blob content
        download_stream = blob_client.download_blob()
        video_content = download_stream.readall()

        # Return the blob content in the HTTP response
        return func.HttpResponse(
            video_content,
            status_code=200,
            mimetype="video/mp4"
        )
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        return func.HttpResponse(
            "Failed to process video from the provided blob URL.",
            status_code=500
        )