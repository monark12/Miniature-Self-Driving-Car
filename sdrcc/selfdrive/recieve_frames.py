import io
import socket
import struct
import cv2
from PIL import Image
import time
from keras.models import model_from_json
import numpy as np

json_file = open('monark/model.json','r')
loaded_model_json = json_file.read()
json_file.close()

cnn_model = model_from_json(loaded_model_json)
cnn_model.load_weights('monark/model.h5')

server_socket = socket.socket()
server_socket.bind(('192.168.0.6', 8000))
server_socket.listen(0)

connection = server_socket.accept()[0].makefile('rb')
try:
  while True:
    prev_time = time.time()
    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
    if not image_len:
      pass

    image_stream = io.BytesIO()
    image_stream.write(connection.read(image_len))
    image_receive_timestamp = time.time()

    image_stream.seek(0)
    image = np.asarray(Image.open(image_stream).convert('L')).reshape(1,480,640,1) # 'LA' for grayscale

    cnn_model.predict(image)

    print("Prediction took -->", time.time()-prev_time)

finally:
  connection.close()
  server_socket.close()
