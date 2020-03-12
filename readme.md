# API Documentation

##Structure of the API
Transforming an image through the API is generally done via two requests. The first request is to upload a string f



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


#### /api/get-formula (GET)
#### /api/update-formula/{guid} (PUT) 
#### /api/remove-formula/{guid} (DELETE)
#### /api/process-image/{guid} (POST)
POSTing image data to a valid guid endpoint will result in the transforms of that GUID being applied to the image, and the result is a returned image that can then be saved locally.
```
curl -F img=@0.jpg http://localhost:5000/api_example > output_img.jpg
```

