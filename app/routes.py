from flask import request, send_file, jsonify
from PIL import Image, ImageOps
from . import app
import io
import uuid
from flask_api import status
import pickledb

ALLOWED_FORMATS = ['jpeg']
VALID_COMMAND_PREFIXES = ('horz', 'vert', 'rotate', 'gray', 'size', 'thumb', 'rleft', 'rright')

db = pickledb.load('formula_db.db', True)
#the spec:
#use rpc's to do the image processor
#user posts a sequence of verbs that describe the image 'recipe' including input types
#image recipes are stored server side and returned quickly
#user then submits a put request to the resource
#image processing transforms tokenized and called in a sequence

#/api/define
#/api/recipeID/transform

#tranforms:
#horz vert rotateN gray resizeNxN thumbN rleft rright

#rotations are CCW so rleft and rright are 90 and 270 respectively
def flip_vert(img):
    return(ImageOps.flip(img))

def flip_horz(img):
    return(ImageOps.mirror(img))

def rotate_angle(img, rotation):
    return(img.rotate(rotation))

def grayscale(img):
    return(ImageOps.grayscale(img))

def resize(img, w, h):
    return(img.resize((w,h)))

def thumbnail(img, s):
    return(img.thumbnail(s))

def process_image(image, instruction_set):
    processed_image = image
    for command in instruction_set:
        if command.startswith('resize'):
            resize_params = command.split('resize')[1].split('x')
            w, h = resize_params
            processed_image = resize(processed_image, int(w), int(h))
        if command.startswith('thumb'):
            size = int(command.split('thumb')[1])
            thumbnail(processed_image, (size, size))
        if command.startswith('rotate'):
            angle = int(command.split('rotate')[1])
            processed_image = rotate_angle(processed_image, angle)
        if command == 'horz':
            processed_image = flip_horz(processed_image)
        if command == 'vert':
            processed_image = flip_vert(processed_image)
        if command == 'gray':
            processed_image = grayscale(processed_image)
        if command == 'rleft':
            processed_image = rotate_angle(processed_image, 90)
        if command == 'rleft':
            processed_image = rotate_angle(processed_image, 270)
    return processed_image



#Return none if there's an issue parsing a string and boot it back
def parse_command_string(command_string):
    command_list = command_string.split(' ')
    print(command_list)
    for idx in range(len(command_list)):
        command = command_list[idx]
        # try:
        if command.startswith('resize'):
            print('resize')
            resize_params = command.split('resize', maxsplit=1)[1].split('x', maxsplit=1)
            print(resize_params)
            validated_command = 'resize' + str(int(resize_params[0])) + 'x' + str(int(resize_params[1]))
            print(validated_command)
            command_list[idx] = validated_command
        elif command.startswith('thumb'):
            numeric_param = command.split('thumb', maxsplit=1)[1]
            validated_command = 'thumb' + str(int(numeric_param))
            command_list[idx] = validated_command
        elif command.startswith('rotate'):
            numeric_param = command.split('rotate', maxsplit=1)[1]
            validated_command = 'rotate' + str(int(numeric_param))

            command_list[idx] = validated_command
        else:
            if command not in VALID_COMMAND_PREFIXES:
                print('nothing found for ' + command)
                return None
        # except:
        #     return None
    print(command_list)
    return(command_list)



@app.route('/api/process-image/<imgURI>', methods=['POST'])
def image_pipeline(imgURI):
    data = db.get(imgURI)
    if not data:
        return({'Error': 'Not Found'}, status.HTTP_404_NOT_FOUND)
    else:
        file_format, formula = data
        image_bytes = request.files.get('img', '')
        proc_image = Image.open(image_bytes)
        proc_image = process_image(proc_image, instruction_set=formula)
        byteio =io.BytesIO()
        proc_image.save(byteio, file_format, quality=95)
        #load image, apply transforms then save to temp and pass to send file
        #proc_image.save(os.path.join(os.getcwd(), 'app/tmp/testimage.jpg'), quality=90)
        byteio.seek(0)
        return(send_file(byteio, mimetype='image/{}'.format(file_format)))

@app.route('/api/get-formula/<imgURI>')
def get_formula(imgURI):
    print('got here')
    data = db.get(imgURI)
    print(data)
    if data:
        return jsonify(Success=imgURI, formula=data[0], commands=data[1])
    else:
        return({'Error': 'Not Found'}, status.HTTP_404_NOT_FOUND)

@app.route('/api/remove-formula/<imgURI>', methods=['DELETE'])
def remove_formula(imgURI):
    if not db.get(imgURI):
        return({'Error': 'Not Found'}, status.HTTP_404_NOT_FOUND)
    else:
        if db.rem(imgURI):
            return({'Success': 'Deleted {}'.format(imgURI)}, status.HTTP_200_OK)
        else:
            return({'Error': 'Unknown server error'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.route('/api/update-formula/<imgURI>', methods=['PUT'])
def update_formula(imgURI):
    if not db.get(imgURI):
        return({'Error': 'Not Found'},status.HTTP_404_NOT_FOUND)
    else:
        formula = request.get_json()
        if 'format' not in formula.keys() or formula['format'] == '':
            return ({'Error': 'Missing or Empty formula parameter'}, status.HTTP_400_BAD_REQUEST)
        if formula['format'] not in ALLOWED_FORMATS:
            return ({'Error': 'Format not supported'}, status.HTTP_501_NOT_IMPLEMENTED)
        if 'commands' not in formula.keys() or formula['commands'] == '':
            return ({'Error': 'Missing or Empty commands Parameter'}, status.HTTP_400_BAD_REQUEST)
        command_list = parse_command_string(formula['commands'])
        if command_list is None or len(command_list) == 0:
            return ({'Error': 'Invalid command string'}, status.HTTP_400_BAD_REQUEST)

        if db.set(imgURI, (formula['format'], command_list)):
            return({'Success': 'Updated {}'.format(imgURI)}, status.HTTP_200_OK)
        else:
            return({'Error': 'Unknown server error'},status.HTTP_500_INTERNAL_SERVER_ERROR)



@app.route('/api/create-formula', methods=['POST'])
def create_formula():
    #expects application/json mimetype
    formula = request.get_json()
    if 'format' not in formula.keys() or formula['format'] == '':
        return ({'Error': 'Missing or Empty formula parameter'}, status.HTTP_400_BAD_REQUEST)
    if formula['format'] not in ALLOWED_FORMATS:
        return ({'Error': 'Format not supported'}, status.HTTP_501_NOT_IMPLEMENTED)
    if 'commands' not in formula.keys() or formula['commands'] == '':
        return ({'Error': 'Missing or Empty commands Parameter'}, status.HTTP_400_BAD_REQUEST)
    command_list = parse_command_string(formula['commands'])
    if command_list is None or len(command_list) == 0:
        return ({'Error': 'Invalid command string'}, status.HTTP_400_BAD_REQUEST)
    command_list = parse_command_string(formula['commands'])

    command_key = str(uuid.uuid4())
    if db.set(command_key, (formula['format'], command_list)):
        return({'Success':  command_key}, status.HTTP_200_OK)
    else:
        return({'Error': 'Unknown server error'}, status.HTTP_500_INTERNAL_SERVER_ERROR)


