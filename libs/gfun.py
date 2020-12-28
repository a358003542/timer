#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import sys


def beep(a, b):
    """make a sound , ref:\
     http://stackoverflow.com/questions/16573051/python-sound-alarm-when-code-finishes
    you need install  ``apt-get install sox``

    :param a: frenquency
    :param b: duration

    create a background thread,so this function does not block the main program
    """
    if sys.platform == "win32":
        import winsound

        def _beep(a, b):
            winsound.Beep(a, b * 1000)
    elif sys.platform == 'linux':
        def _beep(a, b):
            os.system(
                'play --no-show-progress --null \
                --channels 1 synth {0} sine {1}'.format(b, float(a)))
    from threading import Thread
    thread = Thread(target=_beep, args=(a, b))
    thread.daemon = True
    thread.start()