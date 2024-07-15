import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="overlayvideo")
def overlayvideo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # log out the request body 
    logging.info(req.get_body())

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid request body. Please provide a valid JSON.",
            status_code=400
        )

    blob_url = req_body.get('blob_url')
    if not blob_url:
        return func.HttpResponse(
            "Please provide a blob_url in the request body.",
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

        # Upload the video to a different blob storage folder
        destination_blob_url = os.getenv('DESTINATION_BLOB_URL')
        destination_blob_client = blob_service_client.get_blob_client(destination_blob_url)
        
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