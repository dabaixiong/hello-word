import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

# video codec section
gst = "nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)I420, framerate=(fraction)24/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)I420 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
cap = cv2.VideoCapture(gst)
if (cap.isOpened()== False):
  print("Error opening video stream or file")


path_to_ckpt = '/home/nvidia/data/projects/object-detection-tensorflow/ssd_mobilenet_v1_coco_2017_11_17/frozen_inference_graph.pb'
path_to_labels='/home/nvidia/data/projects/tensorflow-object-detection-api/models/research/object_detection/data/mscoco_label_map.pbtxt'
NUM_CLASSES=90


from utils import label_map_util
from utils import visualization_utils as vis_util

detection_graph=tf.Graph()


with detection_graph.as_default():
    od_graph_def=tf.GraphDef()
    with tf.gfile.GFile(path_to_ckpt,'rb') as fid:
        serialized_graph=fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def,name='')


label_map = label_map_util.load_labelmap(path_to_labels)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def load_image():
    ret, frame = cap.read()
    array = frame
    array=array.astype(np.uint8)
    return array

test_image_path=[os.path.join('/home/nvidia/data/projects/tensorflow-object-detection-api/models/research/object_detection/test_images','image{}.jpg'.format(i)) for i in range(1,2)]

show_size=(12,8)
i = 0

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        image_tensor=detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes=detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores=detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes=detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections=detection_graph.get_tensor_by_name('num_detections:0')

        while(cap.isOpened()):
            	vector_image = load_image()
            	vector_image_hd = np.expand_dims(vector_image,axis=0)
            	(boxes,scores,classes,num)=sess.run([detection_boxes,detection_scores,detection_classes,num_detections],feed_dict={image_tensor:vector_image_hd})
            
        	# visualization
        	vis_util.visualize_boxes_and_labels_on_image_array(
            		vector_image,
            		np.squeeze(boxes),
            		np.squeeze(classes).astype(np.int32),
            		np.squeeze(scores),
            		category_index,
            		use_normalized_coordinates=True,
            		line_thickness=5)

        	cv2.imshow('Frame',vector_image)
		
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break

cap.release()
cv2.destroAllWindows()


