import io
import socket
import struct
import cv2
from PIL import Image
import time
import os
os.environ['KERAS_BACKEND'] = 'theano'
from keras.models import model_from_json
import numpy as np

json_file = open('monark/model.json','r')
loaded_model_json = json_file.read()
json_file.close()

cnn_model = model_from_json(loaded_model_json)
cnn_model.load_weights('monark/model.h5')

######recieving
server_socket = socket.socket()
server_socket.bind(('192.168.0.4', 8000))
server_socket.listen(0)
#######

connection = server_socket.accept()[0].makefile('rb')

# wait for server socket to start
time.sleep(2)

#####sending
client_socket = socket.socket()
client_socket.connect(('192.168.0.5', 8001))
print('client connection with server')
#######

send_connection = client_socket.makefile('wb')

try:
  while True:
    prev_time = time.time()
    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]

    image_stream = io.BytesIO()
    image_stream.write(connection.read(image_len))

    image_stream.seek(0)
    image = np.asarray(Image.open(image_stream).convert('L')).reshape(1,480,640,1) # 'LA' for grayscale
    #image = np.asarray(Image.open(image_stream))
    #image = cv2.cvtColor(image, cv2.BGR2GRAY)
    print(image_stream)

    pred = cnn_model.predict(image)[0][0]
    if pred > 1:
      pred = 1
    elif pred < 1:
      pred = -1
    client_socket.send("{0:.2f}".format(pred).encode())
    print("Sent Pred -->", pred)

    print("Prediction took -->", time.time()-prev_time)

  
finally:
  connection.close()
  server_socket.close()
