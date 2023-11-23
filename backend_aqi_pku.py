#!/usr/bin/env python
# coding: utf-8

# # Back-end AQI PKU

from __future__ import division, print_function

import sys, os, glob, re
import numpy as np

from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

import flask
from flask import request
import pandas as pd
import tensorflow as tf
import keras
import numpy as np
import random
import os
from os.path import join, dirname, realpath
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename


from pyngrok import ngrok
import joblib
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

ngrok.set_auth_token("2OPLwHC1DlwnMMKNK9vi9RFTw4r_EwSrAZbWiR25Hnd2M23J")

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # Ganti '*' dengan domain yang sesuai
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

# Load the machine learning model from the .pkl file
model = joblib.load('model_rfc_pku_aqi.pkl')

run_with_ngrok(app)

@app.route('/', methods=['GET'])
def index():
    return "<center><div><h1>Backend AQI RIAU is Online!</h1><image src='https://thumbs.gfycat.com/InfiniteRemarkableDesertpupfish-size_restricted.gif'></image></div></center>"

@app.route('/predictudara', methods=['POST'])
def predict():
    data = {"success": False}
    try:
        if request.method == 'POST':
            pm10 = float(request.form['pm10'])
            pm25 = float(request.form['pm25'])
            so2 = float(request.form['so2'])
            co = float(request.form['co'])
            o3 = float(request.form['o3'])
            no2 = float(request.form['no2'])

            # Create a feature vector from the input data (assuming your model expects a specific format)
            input_data = [pm10, pm25, so2, co, o3, no2]

            # Make a prediction using the loaded model
            prediction = model.predict([input_data])

            result = ''
            ket = ''
            mitigasi = ''
            label = 0
            max_value = max(input_data)
            parm_max = ["pm25", "pm10", "so2", "co", "o3", "no2"][input_data.index(max_value)]

            if 201 <= max_value <= 300:
                result = "Sangat Tidak Sehat"
                ket = "Tingkat kualitas udara yang dapat meningkatkan resiko kesehatan pada sejumlah segmen populasi yang terpapar."
                mitigasi = "Kelompok sensitif: Hindari semua aktivitas di luar. Perbanyak aktivitas di dalam ruangan atau lakukan penjadwalan ulang pada waktu dengan kualitas udara yang baik. Setiap orang: Hindari aktivitas fisik yang terlalu lama di luar ruangan, pertimbangkan untuk melakukan aktivitas di dalam ruangan."
                label = 3

            elif max_value >= 301:
                result = "Berbahaya"
                ket = "Tingkat kualitas udara yang dapat merugikan kesehatan serius pada populasi dan perlu penanganan cepat."
                mitigasi = "Tingkat kualitas udara yang dapat merugikan kesehatan serius pada populasi dan perlu penanganan cepat."
                label = 4
            else:
                if prediction[0] == 0:
                    result = "Baik"
                    ket = "Tingkat kualitas udara yang sangat baik, tidak memberikan efek negatif terhadap manusia, hewan, tumbuhan."
                    mitigasi = "Sangat baik melakukan kegiatan di luar"
                    label = 0
                elif prediction[0] == 1:
                    result = "Sedang"
                    ket = "Tingkat kualitas udara masih dapat diterima pada kesehatan manusia, hewan dan tumbuhan."
                    mitigasi = "Kelompok sensitif: Kurangi aktivitas fisik yang terlalu lama atau berat. Setiap orang: Masih dapat beraktivitas di luar"
                    label = 1
                elif prediction[0] == 2:
                    result = "Tidak Sehat"
                    ket = "Tingkat kualitas udara yang bersifat merugikan pada manusia, hewan dan tumbuhan."
                    mitigasi = "Kelompok sensitif: Boleh melakukan aktivitas di luar, tetapi mengambil rehat lebih sering dan melakukan aktivitas ringan. Amati gejala berupa batuk atau nafas sesak. Penderita asma harus mengikuti petunjuk kesehatan untuk asma dan menyimpan obat asma. Penderita penyakit jantung: gejala seperti palpitasi/jantung berdetak lebih cepat, sesak nafas, atau kelelahan yang tidak biasa mungkin mengindikasikan masalah serius. Setiap orang: Mengurangi aktivitas fisik yang terlalu lama di luar ruangan."
                    label = 2

            data['success'] = True
            data['result'] = result
            data['label'] = label
            data['max'] = max_value
            data['parm_max'] = parm_max
            data['ket'] = ket
            data['mitigasi'] = mitigasi
            print(data)
        else:
            data['success'] = False
            data['result'] = 'Gagal melakukan prediksi'
            data['label'] = 99

    except Exception as e:
        data['error'] = str(e)

    return jsonify(data)

if __name__ == '__main__':
    app.run()

