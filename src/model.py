import matplotlib.pyplot as plt
import numpy as np
from __future__ import absolute_import, division, print_function
# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import os
import re

def draw(actual_times, Predicted_times):
	from scipy.stats import pearsonr

	actual_times = test_labels[:,0]
	predicted_times = predictions[:,0]

	print('R = '+str(pearsonr(actual_times, predicted_times)[1]))

	plt.scatter(actual_times,predicted_times, alpha=0.1)
	plt.xlabel('Actual Age')
	plt.ylabel('Predicted Age')
	plt.show()




if __name__ == "__main__":
	image_folders = [filename for filename in os.listdir('./sub_images/')]

	all_data = []
	labels = []
	times = []
	normals = []
	shears = []
	indices = []

	for folder in image_folders:
	    # Get 3D matrix of data
	    data = []
	    label = []
	    for filename in os.listdir('./sub_images/'+folder+'/'):
	        if 'image' in filename:
	            data.append(np.loadtxt('./sub_images/'+folder+'/'+filename, delimiter=',')) # read in img
	            result = re.search('image(.*)x', filename) # get label from img filename
	            label.append(float(result.group(1))) 
	    all_data.append(data) # collect datas
	    labels.append(label)
	    stats = np.loadtxt('./sub_images/'+folder+'/folder_stats.csv', delimiter=',')
	    # Append stats
	    indices.append(stats[:,0])
	    times.append(stats[:,1])
	    shears.append(stats[:,2])
	    normals.append(stats[:,3])



	    # Obtain target labels
	time_labels = []
	normal_labels = []
	shear_labels = []
	for i, label in enumerate(labels):
	    time_label = []
	    normal_label = []
	    shear_label = []
	    for lab in label:
	        j = np.where(indices[i] == lab)
	        time_label.append(times[i][j][0])
	        normal_label.append(normals[i][j][0])
	        shear_label.append(shears[i][j][0])
	    time_labels.append(time_label)
	    normal_labels.append(normal_label)
	    shear_labels.append(shear_label)



	 # Assemble targets, shuffle data, and assign training and testing sets

	for idx, data in enumerate(all_data):
	    # Get data in right shape
	    targets = np.vstack((time_labels[idx],normal_labels[idx],shear_labels[idx])).T
	    data = np.dstack(data).T

	    # Shuffle data and labels
	    s = np.arange(data.shape[0])
	    np.random.shuffle(s)
	    threeD_data = data[s,:,:]
	    targets = targets[s,:]

	    # Split train and test
	    train_size = round(0.8*data.shape[0])
	    train_data = data[:train_size,:,:]
	    test_data = data[train_size:,:,:]
	    train_labels = targets[:train_size,:]
	    test_labels = targets[train_size:,:]