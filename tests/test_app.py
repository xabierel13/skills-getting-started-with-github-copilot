"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities state before each test"""
    from src.app import activities
    
    # Save original state
    original = {k: {"participants": v["participants"].copy()} for k, v in activities.items()}
    
    yield
    
    # Restore original state
    for activity_name, activity in activities.items():
        activity["participants"] = original[activity_name]["participants"].copy()


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_fields(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club activity exists"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Chess Club" in activities
        assert activities["Chess Club"]["max_participants"] == 12


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200_on_success(self, client, reset_activities):
        """Test that signup returns status 200 on success"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to activity"""
        email = "test@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Basketball Team"]["participants"])
        
        # Sign up
        client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        
        # Get updated count
        response = client.get("/activities")
        new_count = len(response.json()["Basketball Team"]["participants"])
        
        assert new_count == initial_count + 1
        assert email in response.json()["Basketball Team"]["participants"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        result = response.json()
        
        assert "message" in result
        assert "test@mergington.edu" in result["message"]
        assert "Basketball Team" in result["message"]
    
    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_with_spaces_in_activity_name(self, client, reset_activities):
        """Test that signup works with spaces in activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=new@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert "new@mergington.edu" in activities_response.json()["Programming Class"]["participants"]
    
    def test_multiple_signups_to_same_activity(self, client, reset_activities):
        """Test that multiple participants can sign up to same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Basketball%20Team/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball Team"]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_returns_200_on_success(self, client, reset_activities):
        """Test that unregister returns status 200 on success"""
        email = "michael@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity"""
        email = "michael@mergington.edu"
        
        # Verify participant exists
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
    
    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        email = "michael@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        result = response.json()
        
        assert "message" in result
        assert "Unregistered" in result["message"]
        assert email in result["message"]
    
    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        """Test that unregistering non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test that multiple participants can be unregistered"""
        activity = "Chess Club"
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in emails_to_remove:
            response = client.delete(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        for email in emails_to_remove:
            assert email not in participants


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
