# TODO neural net in parallel with multiprocessing
from simplemc.DriverMC import DriverMC
#import tensorflow as tf

# inputs = tf.keras.Input(shape=(3,))
# x = tf.keras.layers.Dense(300, activation=tf.nn.relu)(inputs)
# outputs = tf.keras.layers.Dense(1, activation=tf.nn.relu)(x)
# model = tf.keras.Model(inputs=inputs, outputs=outputs)

analyzer = DriverMC(analyzername="nested", model="owaCDM", datasets="HD+SN+BBAO+Planck", chainsdir="chains")

# analyzer.nestedRunner(nlivepoints=50)
analyzer.nestedRunner(neuralNetwork=True, nlivepoints=50, proxy_tolerance=1.0, ntrain=50,
                       it_to_start_net=50, updInt=50, epochs=300, numNeurons=200, split=0.8)
analyzer.postprocess()  

# analyzer = DriverMC(iniFile='baseConfig.ini')
# analyzer.executer()
# analyzer.postprocess()