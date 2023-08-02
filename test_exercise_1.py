import unittest
from exercise_1 import app

class TestUserAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    def test_get_all_users(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_users_by_id(self):
        # Test existing employee
        response = self.app.get('/user/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], 1)

        # Test non-existing user
        response = self.app.get('/user/100')
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json['message'])


if __name__ == '__main__':
    unittest.main()
