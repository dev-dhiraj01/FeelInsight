import requests
import sys
import json
from datetime import datetime
import time

class SentimentAnalysisAPITester:
    def __init__(self, base_url="https://feelinsight.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{int(time.time())}@example.com"
        self.test_user_password = "TestPass123!"
        self.test_user_name = "Test User"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": self.test_user_email,
                "name": self.test_user_name,
                "password": self.test_user_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"   Token received: {self.token[:20]}...")
            return True
        return False

    def test_duplicate_registration(self):
        """Test duplicate user registration should fail"""
        success, response = self.run_test(
            "Duplicate Registration (Should Fail)",
            "POST",
            "auth/register",
            400,
            data={
                "email": self.test_user_email,
                "name": self.test_user_name,
                "password": self.test_user_password
            }
        )
        return success

    def test_user_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_user_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"   New token received: {self.token[:20]}...")
            return True
        return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        return self.run_test(
            "Invalid Login (Should Fail)",
            "POST",
            "auth/login",
            401,
            data={
                "email": self.test_user_email,
                "password": "wrongpassword"
            }
        )

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        if success and response.get('email') == self.test_user_email:
            print(f"   User verified: {response.get('name')} ({response.get('email')})")
            return True
        return False

    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        test_texts = [
            "I am so happy and excited about this wonderful day!",
            "I feel terrible and sad about everything going wrong.",
            "This is just a normal day with nothing special happening."
        ]
        
        analysis_ids = []
        
        for i, text in enumerate(test_texts):
            success, response = self.run_test(
                f"Sentiment Analysis {i+1}",
                "POST",
                "sentiment/analyze",
                200,
                data={
                    "text": text,
                    "include_emotions": True
                }
            )
            
            if success and 'analysis' in response:
                analysis = response['analysis']
                analysis_ids.append(analysis['analysis_id'])
                print(f"   Sentiment: {analysis['sentiment_label']} (Score: {analysis['sentiment_score']})")
                print(f"   Keywords: {analysis['keywords']}")
                
                # Wait a bit for AI processing
                time.sleep(2)
            else:
                return False
                
        return len(analysis_ids) == len(test_texts)

    def test_empty_text_analysis(self):
        """Test sentiment analysis with empty text should fail"""
        return self.run_test(
            "Empty Text Analysis (Should Fail)",
            "POST",
            "sentiment/analyze",
            400,
            data={
                "text": "",
                "include_emotions": True
            }
        )

    def test_sentiment_history(self):
        """Test getting sentiment analysis history"""
        success, response = self.run_test(
            "Get Sentiment History",
            "GET",
            "sentiment/history",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} historical analyses")
            if len(response) > 0:
                print(f"   Latest analysis: {response[0]['sentiment_label']}")
            return True
        return False

    def test_sentiment_stats(self):
        """Test getting sentiment statistics"""
        success, response = self.run_test(
            "Get Sentiment Statistics",
            "GET",
            "sentiment/stats",
            200
        )
        
        if success and 'total_analyses' in response:
            print(f"   Total analyses: {response['total_analyses']}")
            print(f"   Sentiment distribution: {response.get('sentiment_distribution', {})}")
            return True
        return False

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without token"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success = self.run_test(
            "Unauthorized Access (Should Fail)",
            "GET",
            "auth/me",
            401
        )[0]
        
        # Restore token
        self.token = original_token
        return success

def main():
    print("🚀 Starting Sentiment Analysis API Tests")
    print("=" * 50)
    
    tester = SentimentAnalysisAPITester()
    
    # Test sequence
    test_sequence = [
        ("Health Check", tester.test_health_check),
        ("User Registration", tester.test_user_registration),
        ("Duplicate Registration", tester.test_duplicate_registration),
        ("User Login", tester.test_user_login),
        ("Invalid Login", tester.test_invalid_login),
        ("Get Current User", tester.test_get_current_user),
        ("Unauthorized Access", tester.test_unauthorized_access),
        ("Sentiment Analysis", tester.test_sentiment_analysis),
        ("Empty Text Analysis", tester.test_empty_text_analysis),
        ("Sentiment History", tester.test_sentiment_history),
        ("Sentiment Statistics", tester.test_sentiment_stats),
    ]
    
    failed_tests = []
    
    for test_name, test_func in test_sequence:
        try:
            if not test_func():
                failed_tests.append(test_name)
                print(f"❌ {test_name} FAILED")
            else:
                print(f"✅ {test_name} PASSED")
        except Exception as e:
            failed_tests.append(test_name)
            print(f"❌ {test_name} FAILED with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests: {', '.join(failed_tests)}")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())