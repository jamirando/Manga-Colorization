import os       
import cv2
import numpy as np
import keras
from keras.layers import *
from keras.optimizers import *
from keras.models import *
import matplotlib.pyplot as plt
from keras.regularizers import *
from keras.utils import plot_model
from keras.callbacks import TensorBoard
from time import time
from keras.preprocessing.image import ImageDataGenerator
# from gray_model import *
from GAN_models import *
from losses import *


##This is to prevent out of memory error on cuda 10
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.log_device_placement = True
sess = tf.Session(config=config)
tf.keras.backend.set_session(sess)


#seed
seed = 1234
np.random.seed(seed)
tf.set_random_seed(seed)

#dimensions
x_shape = 512
y_shape = 512

batch = 150

#directories
val_set = "../data/validation_set"
data_out = "../data/data_out_test/"

def GetDataset(dataset, rgb ,gray):
    for root, dirs, files in os.walk(dataset):
        for image in files:
            temp = cv2.imread(root+'/'+image)
            temp = cv2.resize(temp, (x_shape, y_shape))
            rgb.append(temp)
            temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
            temp = temp.reshape(temp.shape[0], temp.shape[1], 1)
            gray.append(temp)


#setup models
gen = generator_model(x_shape,y_shape)

disc = discriminator_model(x_shape,y_shape)
disc.trainable = False
advr = advr_model(gen,disc)
advr.compile(loss=['binary_crossentropy',custom_loss_2], loss_weights = [5,100] , optimizer=Adam(lr=2E-4, beta_1=0.9, beta_2=0.999, epsilon=1e-08), metrics=['accuracy'])
advr.summary()

disc.trainable = False
disc.compile(loss=['binary_crossentropy'], optimizer=Adam(lr=2E-4, beta_1=0.9, beta_2=0.999, epsilon=1e-08), metrics=['accuracy'])
disc.summary()

advr.load_weights("../data/data_out/updated.h5")

#setup dataset
val_rgb = []
val_gray = []


print("Loading dataset")
#get dataset
GetDataset(val_set, val_rgb, val_gray)

#convert to numpy array
val_rgb = np.array(val_rgb)
val_gray = np.array(val_gray)

#normalize rgb to match the output range of -1 to 1
val_gray = (val_gray-127.5)/127.5
print("dataset loaded")


gen_image_val_2 = (gen.predict(val_gray, batch_size=8)*127.5)+127.5
gen_image_val = np.zeros((len(gen_image_val_2), gen_image_val_2.shape[1], gen_image_val_2.shape[2], 3))
gen_image_val[:,:,:,:-1] = gen_image_val_2
gen_image_val[:,:,:,2] = ((val_gray[:,:,:,0]*127.5)+127.5)*3  - gen_image_val[:,:,:,0] - gen_image_val[:,:,:,1]

np.clip(gen_image_val,0,255)
for j in range(len(gen_image_val)):
    cv2.imwrite(data_out +str(j)+'.jpg', gen_image_val[j])


