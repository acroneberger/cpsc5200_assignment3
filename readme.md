# API Documentation

## Structure of the API
Transforming an image through the API is generally done via two requests. The first request is to upload JSON payload with two strings describing the format

File Format: At present, only JPEG is supported. Providing other formats results in a  `{Error: Not Yet Supported}` JSON response.

Commands: Commands are entered as a series of verbs separated by whitespace that the API parses and runs sequentially. The following are accepted verbs for the application:
#horz vert rotateN gray resizeNxN thumbN rleft rright
`horz` : Flip the image horizontally
`vert` : Flip the image vertically
`rotateN` : Rotate the image counterclockwise by N degrees, where N is some integer e.g. `rotate60`
`gray` : Convert the image to grayscale
`resizeNxN` : Resize the image to N by N pixels e.g. `resize1500x2500`
`thumbN` : Create a square thumbnail of length N pixels
`rleft` : rotate counterclockwise (left) 90 degrees
`rright` : rotate clockwise (right) 90 degrees

These verbs can be combined in the command string in any length or order. Transformations will be applied reading the commands left to right, with the output of one transform being used as input to the next transform. For instance, the following command string:
`"horz gray resize1000x1000"`
will be interpreted as flip the image horizontally, convert that image to grayscale, and resize that output to 1000x1000 pixels.

Content types: `/api/create-formula` and `/api/update-formula` both expect data to be sent with the content type `application/json`. `/api/process-image` expects image data to be sent with the content type `multipart/form-data`. All endpoints except for `api/process-image` return JSON responses, while `api/process-image` returns image data with the content type set to the MIME type of the image format. At present the only MIME type used on return is `image/jpeg`.

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




#### /api/get-formula{guid} (GET)
Retrieve the formula stored for a given guid. Returns JSON with `{Error: Not Found}` if the resource is not located.
#### /api/update-formula/{guid} (PUT) 
Update the formula stored for a given guid. Takes the same JSON payload format as `create-formula`. If the guid is not found, returns JSON with `{Error: Not Found}`. There is no support for partial updates--whatever transformation data is in the commands will replace the existing data.
```
curl --header "Content-Type: application/json" \
--request PUT \
--data '{"format":"jpeg", "commands":"horz gray resize1000x1000"}' \
http://localhost:5000/update-formula/8784b499-8681-4f47-8daf-ecc90bf27a52
```
will update the existing formula stored at that guid to the new data sent. If successful, returns:
```
{"Success": "Updated 8784b499-8681-4f47-8daf-ecc90bf27a52"}
#### /api/remove-formula/{guid} (DELETE)
Remove a formula (and the given guid). If the guid is successfully deleted, returns a `{Success': 'Deleted {guid}}` JSON message. If not round returns a `{Error: Not Found}` response.
#### /api/process-image/{guid} (POST)
POSTing image data to a valid guid endpoint will result in the transforms of that GUID being applied to the image, and the result is a returned image that can then be saved locally.
```
curl -F img=@local_image.jpg http://localhost:5000/api_example/8784b499-8681-4f47-8daf-ecc90bf27a52 > output_img.jpg
```
Uploading `local_image.jpg` to this URL, (if there is a formula stored there) will apply the formula and return the transformed image `output_img.jpg` which can then be saved through stdout (or the image data can be moved elsewhere).
