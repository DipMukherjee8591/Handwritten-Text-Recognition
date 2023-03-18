'''
Second Model
Works best with small number of epochs. Model tends to overfit after 7 epochs on average.
Accuracy improved by 1. Went from 84% to 85%.

THIS MODEL IS ASS, 85% accuracy my ASS.
'''

import idx2numpy
import numpy as np

data_path = "Dataset/EMNIST"

'''
Using the Extended MNIST dataset.
Dataset contains the following data :
0-9
A-Z
a-z
'''

# Load training data
x_data = idx2numpy.convert_from_file(f"{data_path}/emnist-byclass-train-images-idx3-ubyte")
y_data = idx2numpy.convert_from_file(f"{data_path}/emnist-byclass-train-labels-idx1-ubyte")

# Reshape
x_data = x_data.reshape(x_data.shape[0], x_data.shape[1], x_data.shape[2], 1)

# Configs
learning_rate = 0.0005
train_epochs = 20
train_workers = 20
# Validation split value is the amount for validation data and not the train data
val_split = 0.1
batch_size = 128

# Validation split and shuffle
from sklearn.model_selection import train_test_split

x_train, x_val, y_train, y_val = train_test_split(x_data, y_data, test_size= val_split)

x_train = np.array(x_train)
y_train = np.array(y_train)
x_val = np.array(x_val)
y_val = np.array(y_val)

# Model
import tensorflow as tf

## Path
import time

t = int(time.time())
model_path = f"Models/{t}"

## Normalize the dataset
x_train = tf.keras.utils.normalize(x_train, axis= 1)
x_val = tf.keras.utils.normalize(x_val, axis= 1)

## Define the model
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Conv2D(32, kernel_size= 3, activation= 'relu', input_shape= (28, 28, 1)))
model.add(tf.keras.layers.Conv2D(64, kernel_size= 3, activation= 'relu'))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(128, activation= 'relu'))
model.add(tf.keras.layers.Dense(62, activation= 'softmax'))

## Compile the model
model.compile(
    optimizer = tf.keras.optimizers.Adam(learning_rate = learning_rate),
    loss = 'sparse_categorical_crossentropy',
    metrics = 'accuracy'
)

## Callbacks
earlystopper = tf.keras.callbacks.EarlyStopping(monitor = 'val_loss', patience = 10, verbose = 1)
tb_callback = tf.keras.callbacks.TensorBoard(f"{model_path}/logs", update_freq = 1)
reduceLROnPlat = tf.keras.callbacks.ReduceLROnPlateau(monitor = "val_loss", factor = 0.9, min_delta = 1e-10, patience = 5, verbose = 1, mode = "auto")
checkpoint = tf.keras.callbacks.ModelCheckpoint(f"{model_path}/cp.meow", monitor= 'val_loss', verbose= 1, save_best_only= True, mode= 'min')

## Convert dataset into tensor and handle batches with CPU
'''
This is done as GPU runs out of memory. Tensorflow doesn't handle batches well and tries to load the whole dataset onto GPU.
'''
with tf.device('CPU') :
    train_data = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(batch_size)
    val_data = tf.data.Dataset.from_tensor_slices((x_val, y_val)).batch(batch_size)

## Train the model
model.fit(
    train_data,
    validation_data = val_data,
    epochs = train_epochs,
    callbacks = [earlystopper, tb_callback, reduceLROnPlat, checkpoint],
    workers = train_workers
)

# Save model
model.save(f"{model_path}/model.meow")