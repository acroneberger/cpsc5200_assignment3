# API Documentation

## Structure of the API
Transforming an image through the API is generally done via two requests. The first request is to upload JSON payload with two strings describing the format of the data



The following are all valid endpoints for interacting with the API:

#### /api/create-formula (POST)
Upload a formula to the server via POST request. The request must provide a JSON payload with two required fields: `format` and `commands`. 

```
curl --header "Content-Type: application/json" \
--request POST \
--data '{"format":"jpeg", "commands":"horz gray resize1000x1000 rotate20 rotate75 vert"}' \
http://localhost:5000/api/create-formula

```
Returns
```
{"Success":"8784b499-8681-4f47-8daf-ecc90bf27a52"}
```
File Format: At present, only JPEG is supported. Providing other formats results in a  `{Error: Not Yet Supported}` JSON response.

Commands: Commands are entered as a series of verbs separated by whitespace that the API parses and runs sequentially. The following are accepted verbs for the application:



#### /api/get-formula{guid} (GET)
Retrieve the formula stored for a given guid. Returns JSON with `{Error: Not Found}` if the resource is not located.
#### /api/update-formula/{guid} (PUT) 
Update the formula stored for a given guid. Takes the same JSON payload format as `create-formula`. If the guid is not found, returns JSON with `{Error: Not Found}`. There is no support for partial updates--whatever transformation data is in the commands
#### /api/remove-formula/{guid} (DELETE)
Remove a formula (and the given guid). If the guid is successfully deleted, returns a `{Success': 'Deleted {guid}}` JSON message. If not round returns a `{Error: Not Found}` response.
#### /api/process-image/{guid} (POST)
POSTing image data to a valid guid endpoint will result in the transforms of that GUID being applied to the image, and the result is a returned image that can then be saved locally.
```
curl -F img=@0.jpg http://localhost:5000/api_example > output_img.jpg
```

