import subprocess
import time
import unittest

import requests


class MyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # run test listener instance on port 8090
        cls.listener = subprocess.Popen(["python", "listener.py", "-p", "8090"])
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.listener.kill()

    def test_info_request(self):
        url = 'http://localhost:8090/wav-info?wavkey=test_102.wav'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        success_result = {"channel_count": 1, "sample_rate": 22050, "execution_time": 40.0}
        self.assertDictEqual(success_result, response.json())

    def test_no_auth_request(self):
        url = 'http://localhost:8090/wav-info?wavkey=test_102.wav'
        response = requests.get(url)
        self.assertEquals(response.status_code, 401)

    def test_wrong_auth_request(self):
        url = 'http://localhost:8090/wav-info?wavkey=test_102.wav'
        headers = {'Authorization': 'UAR-2018'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 401)

    def test_wrong_url_request(self):
        url = 'http://localhost:8090/wav-info111?wavkey=test_102.wav'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 404)

    def test_wrong_wavkey_info_request(self):
        url = 'http://localhost:8090/wav-info?wavkey=test_1021.wav'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

    def test_wrong_wavkey_format_info_request(self):
        url = 'http://localhost:8090/wav-info?wavkey=test_102.mp3'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

    def test_no_wavkey_info_request(self):
        url = 'http://localhost:8090/wav-info'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

    def test_mp3_to_wav_request(self):
        url = 'http://localhost:8090/mp3-to-wav?wavkey=test_102.wav&mp3key=test_102.mp3'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        success_result = {"file_size": 1766181, "execution_time": 40.0}
        self.assertDictEqual(success_result, response.json())

    def test_mp3_to_wav_wrong_mp3key_request(self):
        url = 'http://localhost:8090/mp3-to-wav?wavkey=test_102.wav&mp3key=test_1021.mp3'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

    def test_mp3_to_wav_no_mp3key_request(self):
        url = 'http://localhost:8090/mp3-to-wav?wavkey=test_102.wav'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

    def test_mp3_to_wav_wrong_mp3key_format_request(self):
        url = 'http://localhost:8090/mp3-to-wav?mp3key=test_102.wav&wavkey=test_102.wav'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

    def test_mp3_to_wav_no_wavkey_request(self):
        url = 'http://localhost:8090/mp3-to-wav?mp3key=test_1021.mp3'
        headers = {'Authorization': 'UAR-2017'}
        response = requests.get(url, headers=headers)
        self.assertEquals(response.status_code, 500)

