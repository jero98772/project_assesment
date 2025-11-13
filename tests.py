import unittest
import requests
import json
import os
import tempfile
from io import BytesIO


class APITestCase(unittest.TestCase):
    """Unit tests for the API endpoints"""
    
    BASE_URL = "http://127.0.0.1:9601"
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are used by all tests"""
        cls.test_user = {
            "login": "testuser",
            "email": "testuser@test.com",
            "password": "testpass123",
            "password_repeat": "testpass123"
        }
        cls.session = requests.Session()
        cls.project_id = None
        cls.document_id = None
    
    def test_01_register(self):
        """Test user registration"""
        response = requests.post(
            f"{self.BASE_URL}/auth",
            headers={"Content-Type": "application/json"},
            json=self.test_user
        )
        self.assertIn(response.status_code, [200, 201, 409])  # 409 if user exists
    
    def test_02_login(self):
        """Test user login"""
        login_data = {
            "login": self.test_user["login"],
            "password": self.test_user["password"]
        }
        response = self.session.post(
            f"{self.BASE_URL}/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        self.assertIn(response.status_code, [200, 201])
        # Verify cookies are set
        self.assertTrue(len(self.session.cookies) > 0)
    
    def test_03_create_project(self):
        """Test project creation"""
        project_data = {
            "name": "Test Project",
            "description": "A test project for unit testing"
        }
        response = self.session.post(
            f"{self.BASE_URL}/projects",
            headers={"Content-Type": "application/json"},
            json=project_data
        )
        self.assertIn(response.status_code, [200, 201])
        
        # Store project ID for later tests
        data = response.json()
        if 'id' in data:
            self.__class__.project_id = data['id']
        elif 'project_id' in data:
            self.__class__.project_id = data['project_id']
    
    def test_04_get_all_projects(self):
        """Test retrieving all projects"""
        response = self.session.get(f"{self.BASE_URL}/projects")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, (list, dict))
    
    def test_05_get_project_info(self):
        """Test retrieving project information"""
        if not self.project_id:
            self.skipTest("No project ID available")
        
        response = self.session.get(
            f"{self.BASE_URL}/project/{self.project_id}/info"
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('name', data)
    
    def test_06_update_project_info(self):
        """Test updating project information"""
        if not self.project_id:
            self.skipTest("No project ID available")
        
        update_data = {
            "name": "Updated Test Project",
            "description": "Updated description for testing"
        }
        response = self.session.put(
            f"{self.BASE_URL}/project/{self.project_id}/info",
            headers={"Content-Type": "application/json"},
            json=update_data
        )
        self.assertIn(response.status_code, [200, 204])
    
    def test_07_upload_documents(self):
        """Test document upload"""
        if not self.project_id:
            self.skipTest("No project ID available")
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for unit testing.")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                files = {'files': ('test_document.txt', f, 'text/plain')}
                response = self.session.post(
                    f"{self.BASE_URL}/project/{self.project_id}/documents",
                    files=files
                )
            
            self.assertIn(response.status_code, [200, 201])
            
            # Store document ID for later tests
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                self.__class__.document_id = data[0].get('id') or data[0].get('document_id')
            elif isinstance(data, dict):
                self.__class__.document_id = data.get('id') or data.get('document_id')
        
        finally:
            os.unlink(temp_file)
    
    def test_08_get_documents(self):
        """Test retrieving documents"""
        if not self.project_id:
            self.skipTest("No project ID available")
        
        response = self.session.get(
            f"{self.BASE_URL}/project/{self.project_id}/documents"
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, (list, dict))
    
    def test_09_download_document(self):
        """Test document download"""
        if not self.document_id:
            self.skipTest("No document ID available")
        
        response = self.session.get(
            f"{self.BASE_URL}/document/{self.document_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 0)
    
    def test_10_update_document_filename(self):
        """Test updating document filename only"""
        if not self.document_id:
            self.skipTest("No document ID available")
        
        data = {'original_filename': 'renamed_test_document.txt'}
        response = self.session.put(
            f"{self.BASE_URL}/document/{self.document_id}",
            data=data
        )
        self.assertIn(response.status_code, [200, 204])
    
    def test_11_update_document_with_file(self):
        """Test updating document with new file and filename"""
        if not self.document_id:
            self.skipTest("No document ID available")
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is updated content for the test document.")
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                files = {'file': ('updated_document.txt', f, 'text/plain')}
                data = {'original_filename': 'updated_test_document.txt'}
                response = self.session.put(
                    f"{self.BASE_URL}/document/{self.document_id}",
                    files=files,
                    data=data
                )
            
            self.assertIn(response.status_code, [200, 204])
        
        finally:
            os.unlink(temp_file)
    
    def test_12_delete_document(self):
        """Test document deletion"""
        if not self.document_id:
            self.skipTest("No document ID available")
        
        response = self.session.delete(
            f"{self.BASE_URL}/document/{self.document_id}"
        )
        self.assertIn(response.status_code, [200, 204])
    
    def test_13_delete_project(self):
        """Test project deletion"""
        if not self.project_id:
            self.skipTest("No project ID available")
        
        response = self.session.delete(
            f"{self.BASE_URL}/project/{self.project_id}"
        )
        self.assertIn(response.status_code, [200, 204])


class APIErrorTestCase(unittest.TestCase):
    """Test error handling and edge cases"""
    
    BASE_URL = "http://127.0.0.1:9601"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "login": "nonexistent_user",
            "password": "wrong_password"
        }
        response = requests.post(
            f"{self.BASE_URL}/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        self.assertIn(response.status_code, [401, 403, 404])
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        response = requests.get(f"{self.BASE_URL}/projects")
        self.assertIn(response.status_code, [401, 403])
    
    def test_invalid_project_id(self):
        """Test accessing non-existent project"""
        session = requests.Session()
        # Login first
        login_data = {"login": "testuser", "password": "testpass123"}
        session.post(
            f"{self.BASE_URL}/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        response = session.get(f"{self.BASE_URL}/project/99999/info")
        self.assertIn(response.status_code, [404, 403])
    
    def test_register_duplicate_user(self):
        """Test registering with existing credentials"""
        user_data = {
            "login": "testuser",
            "email": "testuser@test.com",
            "password": "testpass123",
            "password_repeat": "testpass123"
        }
        response = requests.post(
            f"{self.BASE_URL}/auth",
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        self.assertIn(response.status_code, [409, 400])
    
    def test_password_mismatch(self):
        """Test registration with mismatched passwords"""
        user_data = {
            "login": "newuser",
            "email": "newuser@test.com",
            "password": "password123",
            "password_repeat": "different_password"
        }
        response = requests.post(
            f"{self.BASE_URL}/auth",
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        self.assertIn(response.status_code, [400, 422])


if __name__ == '__main__':
    # Run tests in order
    unittest.main(verbosity=2)