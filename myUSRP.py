# generic USRP code

import uhd
from uhd import libpyuhd as lib
import numpy as np
import threading
from six.moves import queue
import time

from myConstants import *

class Device:

    def __init__(self, serial):
        self.usrp = uhd.usrp.MultiUSRP(serial)
        self.rx_lock = threading.Lock()
        self.tx_lock = threading.Lock()
        self.rx_event = threading.Event()
        self.tx_event = threading.Event()
        self.rx_fifo = queue.Queue(maxsize=nrep)
        self.debug = False
        print('USRP device created (Serial =', serial, ')')

    def chg_tx_freq(self, fc):
        with self.tx_lock:
            # self.tx_fc = fc
            for k in range(len(self.tx_channels)):
                self.usrp.set_tx_freq(lib.types.tune_request(fc), self.tx_channels[k])

        if self.debug:
            print('TX freq changed to', fc)

    def chg_rx_freq(self, fc):
        with self.rx_lock:
            # self.rx_fc = fc
            for k in range(len(self.rx_channels)):
                self.usrp.set_rx_freq(lib.types.tune_request(fc), self.rx_channels[k])

        if self.debug:
            print('RX freq changed to', fc)

    def set_tx_config(self, fc, fs, channels, gains):
        # with self.tx_lock:
        self.tx_fc = fc
        self.tx_fs = fs
        self.tx_channels = channels
        self.tx_gains = gains

        for k in range(len(channels)):
            self.usrp.set_tx_rate(fs, channels[k])
            self.usrp.set_tx_freq(lib.types.tune_request(fc), channels[k])
            self.usrp.set_tx_gain(gains[k], channels[k])

        if self.debug:
            print('TX configured')


    def set_rx_config(self, fc, fs, channels, gains):
        # with self.rx_lock:
        self.rx_fc = fc
        self.rx_fs = fs
        self.rx_channels = channels
        self.rx_gains = gains

        for k in range(len(channels)):
            self.usrp.set_rx_rate(fs, channels[k])
            self.usrp.set_rx_freq(lib.types.tune_request(fc), channels[k])
            self.usrp.set_rx_gain(gains[k], channels[k])

        if self.debug:
            print('RX configured')

    def discard_rx_samples(self, num):
        for k in range(num):
            self.rx_fifo.get()
            # try:
            #     self.rx_fifo.get_nowait()
            # except queue.Empty:
            #     return


    def get_rx_buffer(self):
        return self.rx_fifo.get()


    def start_rx_stream(self):
        with self.rx_lock:
            st_args = lib.usrp.stream_args("fc32", "sc16")
            st_args.channels = self.rx_channels
            self.rx_streamer = self.usrp.get_rx_stream(st_args)

            stream_cmd = lib.types.stream_cmd(lib.types.stream_mode.start_cont)
            stream_cmd.stream_now = (len(self.rx_channels) == 1)
            stream_cmd.time_spec = lib.types.time_spec(self.usrp.get_time_now().get_real_secs() + 0.05)
            self.rx_streamer.issue_stream_cmd(stream_cmd)

        # Thread
        self.rx_thread = threading.Thread(target=self.__rx_loop, args=())
        self.rx_thread.start()

    def stop_rx_stream(self):
        self.rx_event.set()
        self.rx_thread.join()
        if self.debug:
            print('RX join')

        # Cleanup
        self.rx_streamer = None

    def __rx_loop(self):
        if self.debug:
            print('__rx_loop() started')

        with self.rx_lock:
            self.rx_metadata = lib.types.rx_metadata()
            buffer_samps = self.rx_streamer.get_max_num_samps()
            if (ns != buffer_samps):
                print('Buffer size mismatch', ns, buffer_samps)
                return

        recv_buffer = np.zeros(
            (len(self.rx_channels), buffer_samps), dtype=np.complex64)

        while not(self.rx_event.isSet()):
            with self.rx_lock:
                samps = self.rx_streamer.recv(recv_buffer, self.rx_metadata)

                if self.rx_metadata.error_code != lib.types.rx_metadata_error_code.none:
                    if self.debug:
                        print(self.rx_metadata.strerror())

            time.sleep(1e-6) # yield

            try:
                # self.rx_fifo.put_nowait(recv_buffer)
                # FULL COPY needed
                # self.rx_fifo.put_nowait(np.array(recv_buffer, copy=True))
                self.rx_fifo.put_nowait(recv_buffer)
                recv_buffer = np.zeros(
                    (len(self.rx_channels), buffer_samps), dtype=np.complex64)
            except queue.Full:
                pass

        # End of RX msg
        with self.rx_lock:
            stream_cmd = lib.types.stream_cmd(lib.types.stream_mode.stop_cont)
            self.rx_streamer.issue_stream_cmd(stream_cmd)

        # # Clean up buffer
        # while True:
        #     samps = self.rx_streamer.recv(recv_buffer, self.rx_metadata)
        #     if samps == 0:
        #         break

        if self.debug:
            print('__rx_loop() end')

    def start_tx_stream(self, waveform_proto):
        with self.tx_lock:
            st_args = lib.usrp.stream_args("fc32", "sc16")
            st_args.channels = self.tx_channels

            self.tx_streamer = self.usrp.get_tx_stream(st_args)
            buffer_samps = self.tx_streamer.get_max_num_samps()
            proto_len = waveform_proto.shape[-1]

            if proto_len < buffer_samps:
                waveform_proto = np.tile(waveform_proto, (1, int(np.ceil(float(buffer_samps) / proto_len))))
                proto_len = waveform_proto.shape[-1]

            self.tx_metadata = lib.types.tx_metadata()

            if len(waveform_proto.shape) == 1:
                waveform_proto = waveform_proto.reshape(1, waveform_proto.size)
            if waveform_proto.shape[0] < len(self.tx_channels):
                waveform_proto = np.tile(waveform_proto[0], (len(self.tx.channels), 1))

            self.tx_waveform = waveform_proto

        # Thread
        self.tx_thread = threading.Thread(target=self.__tx_loop, args=())
        self.tx_thread.start()

    def stop_tx_stream(self):
        # Stop event
        self.tx_event.set()
        self.tx_thread.join()
        if self.debug:
            print('TX join')

        # Cleanup
        self.tx_streamer = None

    def __tx_loop(self):
        if self.debug:
            print('__tx_loop() start')

        while not(self.tx_event.isSet()):
            with self.tx_lock:
                self.tx_streamer.send(self.tx_waveform, self.tx_metadata)

            time.sleep(1e-6) # yield

        # End of TX msg
        with self.tx_lock:
            self.tx_metadata.end_of_burst = True
            self.tx_streamer.send(0 * self.tx_waveform, self.tx_metadata)

        if self.debug:
            print('__tx_loop() end')


