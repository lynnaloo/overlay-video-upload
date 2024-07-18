from urllib.parse import urlparse
import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import os

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
        blob_client = blob_service_client.get_blob_client(blob_url)
        
        # Download the blob content
        download_stream = blob_client.download_blob()
        video_content = download_stream.readall()

        # Save the video content to a local file (optional, for processing)
        local_file_path = "/tmp/downloaded_video.mp4"
        with open(local_file_path, "wb") as video_file:
            video_file.write(video_content)

        # Process the video content 
        # For example, overlay a watermark on the video
        # tags of objects in the video will be in content_tags

        # Upload the video to a different blob storage folder
        destination_blob_url = os.getenv('DESTINATION_BLOB_URL')
        if not destination_blob_url:
            return func.HttpResponse(
                "Please provide a DESTINATION_BLOB_URL in the environment variables.",
                status_code=500
            )
        
        # Create a blob client using the destination blob URL
        #destination_blob_client = blob_service_client.get_blob_client(destination_blob_url)

        parsed_dest_url = urlparse(destination_blob_url)
        dest_path_parts = parsed_dest_url.path.lstrip('/').split('/')
        dest_container_name = dest_path_parts[0]
        dest_blob_name = '/'.join(dest_path_parts[1:])
        
        # Create a blob client using the destination container and blob name
        destination_blob_client = blob_service_client.get_blob_client(container=dest_container_name, blob=dest_blob_name)

        with open(local_file_path, "rb") as data:
            destination_blob_client.upload_blob(data, overwrite=True)

        # Construct the full URL of the uploaded video
        uploaded_video_url = destination_blob_client.url

        return func.HttpResponse(
            f"Video downloaded and uploaded successfully. URL: {uploaded_video_url}",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        return func.HttpResponse(
            "Failed to process video from the provided blob URL.",
            status_code=500
        )