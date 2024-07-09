import os
import requests
import unittest
import uuid

PAYLOAD = {'name': f"test_{str(uuid.uuid4())}"}
HEADERS = {'accept': 'application/json'}


class TestMinioBucket(unittest.TestCase):
    def setUp(self):
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'http://127.0.0.1:9000')
        self.bucket_name = os.getenv('BUCKET_NAME', 'getmeme')

    def test_check_bucket_exists(self):
        session = requests.Session()
        response = session.get(f"{self.endpoint}/{self.bucket_name}")
        session.close()
        self.assertEqual(response.status_code, 200,
                         ("Bucket в MinIO не создана, "
                          "ее нужно создать вручную скриптом, см.Readme"))


class TestMemesAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://127.0.0.1:8000/api/memes/'

    def test_get_memes(self):
        response = requests.get(self.base_url.rstrip('/'))
        self.assertEqual(response.status_code, 200)

    def test_create_new_meme(self):
        with open('test/test.jpg', 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpg')}
            response = requests.post(
                self.base_url, data=PAYLOAD, files=files, headers=HEADERS)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
