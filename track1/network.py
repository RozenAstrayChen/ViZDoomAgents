# coding: utf-8
# implement neural network here

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import configs as cfg

RNN_DIM = 512


class ACNetwork(object):
    """
    Actor-Critic network
    """
    def __init__(self, scope, optimizer, play=False, img_shape=(80, 80)):
        self.img_shape = img_shape
        self.__create_network(scope, optimizer, play=play)

    def __create_network(self, scope, optimizer, play=False):
        with tf.variable_scope(scope):
            self.inputs = tf.placeholder(shape=[None, *self.img_shape, 1], dtype=tf.float32)
            #self.game_variables = tf.placeholder(shape=[None, 2], dtype=tf.float32)
            self.conv_1 = slim.conv2d(activation_fn=tf.nn.relu, inputs=self.inputs, num_outputs=32,
                                      kernel_size=[8, 8], stride=4, padding='SAME')
            self.conv_2 = slim.conv2d(activation_fn=tf.nn.relu, inputs=self.conv_1, num_outputs=64,
                                      kernel_size=[4, 4], stride=2, padding='SAME')
            self.conv_3 = slim.conv2d(activation_fn=tf.nn.relu, inputs=self.conv_2, num_outputs=64,
                                      kernel_size=[3, 3], stride=1, padding='SAME')
            #self.fc = slim.fully_connected(slim.flatten(self.conv_3), 512, activation_fn=tf.nn.elu)
            self.flatten = slim.flatten(self.conv_3)
            #self.new_fc = tf.concat([self.fc, self.game_variables], axis=1)
            lstm_cell = tf.contrib.rnn.BasicLSTMCell(RNN_DIM, state_is_tuple=True)
            c_init = np.zeros((1, lstm_cell.state_size.c), np.float32)
            h_init = np.zeros((1, lstm_cell.state_size.h), np.float32)
            self.state_init = [c_init, h_init]
            c_in = tf.placeholder(tf.float32, [1, lstm_cell.state_size.c])
            h_in = tf.placeholder(tf.float32, [1, lstm_cell.state_size.h])
            self.state_in = (c_in, h_in)
            rnn_in = tf.expand_dims(self.flatten, [0])
            step_size = tf.shape(self.inputs)[:1]
            state_in = tf.contrib.rnn.LSTMStateTuple(c_in, h_in)
            lstm_outputs, lstm_state = tf.nn.dynamic_rnn(lstm_cell,
                                                         rnn_in,
                                                         initial_state=state_in,
                                                         sequence_length=step_size,
                                                         time_major=False)
            lstm_c, lstm_h = lstm_state
            self.state_out = (lstm_c[:1, :], lstm_h[:1, :])
            rnn_out = tf.reshape(lstm_outputs, [-1, RNN_DIM])

            self.policy = slim.fully_connected(rnn_out,
                                               cfg.ACTION_DIM,
                                               activation_fn=tf.nn.softmax,
                                               biases_initializer=None)
            self.value = slim.fully_connected(rnn_out,
                                              1,
                                              activation_fn=None,
                                              biases_initializer=None)
            if scope != 'global' and not play:
                self.actions = tf.placeholder(shape=[None], dtype=tf.int32)
                self.actions_onehot = tf.one_hot(self.actions, cfg.ACTION_DIM, dtype=tf.float32)
                self.target_v = tf.placeholder(shape=[None], dtype=tf.float32)
                self.advantages = tf.placeholder(shape=[None], dtype=tf.float32)

                self.responsible_outputs = tf.reduce_sum(self.policy * self.actions_onehot, axis=1)

                # Loss functions
                self.policy_loss = -tf.reduce_sum(self.advantages * tf.log(self.responsible_outputs+1e-10))
                self.value_loss = tf.reduce_sum(tf.square(self.target_v - tf.reshape(self.value, [-1])))
                self.entropy = -tf.reduce_sum(self.policy * tf.log(self.policy+1e-10))
                self.loss = self.policy_loss + 0.5 * self.value_loss - 0.1 * self.entropy

                # Get gradients from local network using local losses
                local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope)
                self.gradients = tf.gradients(self.loss, local_vars)
                self.var_norms = tf.global_norm(local_vars)
                grads, self.grad_norms = tf.clip_by_global_norm(self.gradients, 40.0)

                # Apply local gradients to global network
                global_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'global')
                self.apply_grads = optimizer.apply_gradients(zip(grads, global_vars))

                # add summary

    def update_entropy_rate(self, global_step):
        if global_step % cfg.decay_steps == 0:
            self._entropy_rate = cfg.starter_entropy_rate * cfg.decay_rate ** (global_step / cfg.decay_steps)
