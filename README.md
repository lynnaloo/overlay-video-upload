# Upload a video with an overlay

Downloads a video from Azure Blob Storage, processes and adds a watermark, returns the video 

## Create an Azure Blob Storage account with two containers: one to upload existing videos, a second for uploading processes videos

## Add a `local.settings.json` file using this example:

```
  {
    "IsEncrypted": false,
    "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "AZURE_STORAGE_CONNECTION_STRING": "",
  }
}
```

`UseDevelopmentStorage=true` assumes that Azurite is running for local development. For production, this should be a URL to the Blob Storage account for the Azure Function."

## POST HTTP Request to the Function URL with this format:

```
  {
    "blob_url": "",
    "content_tags": "example1, example2"
  }
```
