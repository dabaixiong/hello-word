# script created by Yun Long
# Purpose: a python script to read in a video, perform object detection on movidius NCS, then display the video along
# with the objects bouding boxes
# prerequisite: read SSD paper, understand gstreamer, movidius SDK.
# License: Micron Technology
# Date: 04-18-2018

# Import necessary packages
from mvnc import mvncapi as mvnc
import argparse
import numpy as np
import time
import cv2

# class label
CLASSES = ["background", "aeroplane", "bicycle", "bird",
           "boat", "bottle", "bus", "car", "cat", "chair", "cow",
           "diningtable", "dog", "horse", "motorbike", "person",
           "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# preprocess each frame sampled from the video
def preprocess_frame(input_frame):
    NETWORK_WIDTH = 300
    NETWORK_HEIGHT = 300
    preprocess = cv2.resize(input_frame, (NETWORK_WIDTH, NETWORK_HEIGHT))
    preprocess = preprocess - 127.5
    preprocess = preprocess * 0.007843

    return preprocess


# Here is how the magic works!
def inference(image,graph,time_it, out):

    image = preprocess_frame(image)

    label_text_color = (255, 255, 255)  # white text

    # send graph file to NCS, similar with send the kernel to GPU for execution.
    graph.LoadTensor(image.astype(np.float16),None)
    (output,_) = graph.GetResult()

    # recover the image to 0-1 range
    image = (image + 1) / 2

    # number of detected objects
    num_valid_boxes = int(output[0])
    print('total num boxes: ' + str(num_valid_boxes))

    for box_index in range(num_valid_boxes):
            base_index = 7+ box_index * 7
            if (not np.isfinite(output[base_index]) or
                    not np.isfinite(output[base_index + 1]) or
                    not np.isfinite(output[base_index + 2]) or
                    not np.isfinite(output[base_index + 3]) or
                    not np.isfinite(output[base_index + 4]) or
                    not np.isfinite(output[base_index + 5]) or
                    not np.isfinite(output[base_index + 6])):
                # boxes with non infinite (inf, nan, etc) numbers must be ignored
                print('box at index: ' + str(box_index) + ' has nonfinite data, ignoring it')
                continue

            # overlay boxes and labels on the original image to classify
            add_boxes(image, output[base_index:base_index + 7])


    time_it = time.time() - time_it
    test = cv2.putText(image, 'FPS: ' + str(1 / time_it), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       label_text_color, 1)

    out.write(image)
    cv2.imshow('output', image)


def add_boxes(image, object_info):
    display_image = image
    # the minimal score for a box to be shown
    min_score_percent = 0

    source_image_width = display_image.shape[1]
    source_image_height = display_image.shape[0]

    base_index = 0
    class_id = object_info[base_index + 1]
    percentage = int(object_info[base_index + 2] * 100)

    if (percentage <= min_score_percent):
        # ignore boxes less than the minimum score
        return

    label_text = CLASSES[int(class_id)] + " (" + str(percentage) + "%)"

    box_left = int(object_info[base_index + 3] * source_image_width)
    box_top = int(object_info[base_index + 4] * source_image_height)
    box_right = int(object_info[base_index + 5] * source_image_width)
    box_bottom = int(object_info[base_index + 6] * source_image_height)

    box_color = (255, 128, 0)  # box color
    box_thickness = 2

    cv2.rectangle(display_image, (box_left, box_top), (box_right, box_bottom), box_color, box_thickness)

    # draw the classification label string just above and to the left of the rectangle
    label_background_color = (0, 0, 0)
    label_text_color = (255, 255, 255)  # white text

    label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    label_left = box_left
    label_top = box_top - label_size[1]
    if (label_top < 1):
        label_top = 1
    label_right = label_left + label_size[0]
    label_bottom = label_top + label_size[1]
    cv2.rectangle(display_image, (label_left - 1, label_top - 1), (label_right + 1, label_bottom + 1),
                  label_background_color, -1)

    # label text above the box
    test = cv2.putText(display_image, label_text, (label_left, label_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_text_color, 1)

    # return display_image


def load_frame(cap):

    # load a new frame from the video
    _, frame = cap.read()
    return frame


# I don't like the main function in python, python is not C++!
# find movidius ncs and open the first one. We only have one, so open it.
devices = mvnc.EnumerateDevices()
device = mvnc.Device(devices[0])
device.OpenDevice()

# load graph and allocate some memory on NCS
with open('mobilenetgraph', mode='rb') as f:
    graph_in_memory = f.read()
graph = device.AllocateGraph(graph_in_memory)

# let's first test with an image
# infer_image = cv2.imread('nps_chair.png')
# inference(infer_image, graph)

# now let's make it a bit more complex
cap = cv2.VideoCapture('sample_outdoor_car_1080p_10fps.mp4')
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', -1, 20.0, (300,300))

iter = 0

while (iter < 1000):
    time_it = time.time() # the finish time is inside add_boxes function
    new_frame = load_frame(cap)
    inference(new_frame, graph, time_it, out)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
    iter += 1

# Clean up the graph and the device
graph.DeallocateGraph()
device.CloseDevice()

cap.release()
out.release()
cv2.destroyAllWindows()



