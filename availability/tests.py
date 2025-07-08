from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, Hairdresser
from availability.models import Availability
from datetime import time, datetime, timedelta
import jwt
import json

class CreateAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_url = reverse('create_availability')
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.hairdresser_payload = {
            "email": "rodrigosc615@gmail.com",
            "first_name": "Rodrigo Santos",
            "last_name": "o 12",
            "password": "senha123",
            "phone": "+5592984502890",
            "complement": "casa",
            "neighborhood": "centro",
            "city": "manaus",
            "state": "AM",
            "address": "rua francy assis",
            "number": "2229",
            "postal_code": "69050750",
            "rating": 5,
            "role": "hairdresser",
            "cnpj": "12345678901212",
            "experience_years": 4,
            "resume": "ele é legal e joga bem",
            "preferences": json.dumps([]),
            'experience_time':'experience_time',
            'experiences':'experiences',
            'products':'products',
            'resume':'resume'
        }
        
    def test_create_availability_success(self):
        # Register hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Login
        login_payload = {
            'email': 'rodrigosc615@gmail.com',
            'password': 'senha123'
        }

        response = self.client.post(
            self.login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Create availability
        response_creation = self.client.post(
            self.create_url,
            data=json.dumps({
                'weekday': 'monday',
                'start_time': '09:00:00',
                'end_time': '17:00:00'
            }),
            content_type='application/json'
        )

        self.assertEqual(response_creation.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.count(), 1)
        availability = Availability.objects.first()
        self.assertEqual(availability.weekday, 'monday')
        self.assertEqual(str(availability.start_time), '09:00:00')
        self.assertEqual(str(availability.end_time), '17:00:00')
    
    def test_create_availability_success_with_break_time(self):
        # Register hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Login
        login_payload = {
            'email': 'rodrigosc615@gmail.com',
            'password': 'senha123'
        }

        response = self.client.post(
            self.login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Create availability
        response_creation = self.client.post(
            self.create_url,
            data=json.dumps({
                'weekday': 'tuesday',
                'start_time': '09:00:00',
                'end_time': '17:00:00',
                'break_start': '12:00:00',
                'break_end': '13:00:00'
            }),
            content_type='application/json'
        )

        self.assertEqual(response_creation.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.count(), 1)

    def test_create_availability_missing_fields(self):
        # Register hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Login
        login_payload = {
            'email': 'rodrigosc615@gmail.com',
            'password': 'senha123'
        }

        self.client.post(
            self.login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Create availability with missing fields
        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'weekday': 'monday',
                # Missing start_time and end_time
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Availability.objects.count(), 0)
    
    def test_create_availability_no_auth(self):
        # Try to create availability without login
        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'weekday': 'monday',
                'start_time': '09:00:00',
                'end_time': '17:00:00'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Availability.objects.count(), 0)

class CreateMultipleAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Hairdresser payload similar to the previous test
        self.hairdresser_payload = {
            "email": "rodrigosc615@gmail.com",
            "first_name": "Rodrigo Santos",
            "last_name": "o 12",
            "password": "senha123",
            "phone": "+5592984502890",
            "complement": "casa",
            "neighborhood": "centro",
            "city": "manaus",
            "state": "AM",
            "address": "rua francy assis",
            "number": "2229",
            "postal_code": "69050750",
            "rating": 5,
            "role": "hairdresser",
            "cnpj": "12345678901212",
            "experience_years": 4,
            "resume": "ele é legal e joga bem",
            "preferences": json.dumps([]),
            'experience_time':'experience_time',
            'experiences':'experiences',
            'products':'products',
            'resume':'resume'
        }
        
        # Register and get hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Login
        login_payload = {
            'email': 'rodrigosc615@gmail.com',
            'password': 'senha123'
        }
        self.client.post(
            self.login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Get the hairdresser object
        self.hairdresser = Hairdresser.objects.get(user__email='rodrigosc615@gmail.com')
        
        # URL for creating multiple availabilities
        self.create_multiple_url = reverse('create_multiple_availability', kwargs={'hairdresser_id': self.hairdresser.id})
    
    def test_create_multiple_availability_success(self):
        # Payload with multiple availabilities
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                },
                {
                    'weekday': 'tuesday',
                    'start_time': '10:00:00',
                    'end_time': '18:00:00',
                    'break_start': '12:00:00',
                    'break_end': '13:00:00'
                }
            ]
        }
        
        # Create multiple availabilities
        response = self.client.post(
            self.create_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.count(), 2)
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 2)
    
    def test_create_multiple_availability_with_duplicate_weekday(self):
        # First create an availability for monday
        first_payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        self.client.post(
            self.create_multiple_url,
            data=json.dumps(first_payload),
            content_type='application/json'
        )
        
        # Try to create another availability for the same weekday
        second_payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '10:00:00',
                    'end_time': '18:00:00'
                }
            ]
        }
        
        response = self.client.post(
            self.create_multiple_url,
            data=json.dumps(second_payload),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Availability.objects.count(), 1)
        self.assertIn('Availability already exists', str(response.content))
    
    def test_create_multiple_availability_missing_fields(self):
        # Payload with missing required fields
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    # Missing start_time and end_time
                }
            ]
        }
        
        response = self.client.post(
            self.create_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Availability.objects.count(), 0)
        self.assertIn('required fields is missing', str(response.content))
    
    def test_create_multiple_availability_invalid_weekday(self):
        # Payload with invalid weekday
        payload = {
            'availabilities': [
                {
                    'weekday': 'invalidday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        response = self.client.post(
            self.create_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Availability.objects.count(), 0)
        self.assertIn('Invalid weekday', str(response.content))
    
    def test_create_multiple_availability_nonexistent_hairdresser(self):
        # Try to create availability for a non-existent hairdresser
        non_existent_url = reverse('create_multiple_availability', kwargs={'hairdresser_id': 9999})
        
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        response = self.client.post(
            non_existent_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Availability.objects.count(), 0)
        self.assertIn('Hairdresser not found', str(response.content))

class ListAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Create hairdresser user
        self.hairdresser_payload = {
            "email": "hairdresser@example.com",
            "first_name": "Hair",
            "last_name": "Dresser",
            "password": "password123",
            "phone": "+5592984502890",
            "complement": "casa",
            "neighborhood": "centro",
            "city": "manaus",
            "state": "AM",
            "address": "Salon Street",
            "number": "123",
            "postal_code": "12345678",
            "rating": 5,
            "role": "hairdresser",
            "cnpj": "12345678901212",
            "experience_years": 5,
            "resume": "Professional hairdresser",
            "preferences": json.dumps([]),
            'experience_time':'experience_time',
            'experiences':'experiences',
            'products':'products',
            'resume':'resume'
        }
        
        # Register hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Get hairdresser
        self.hairdresser = Hairdresser.objects.get(user__email="hairdresser@example.com")
        
        # Create availabilities
        Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='monday',
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='tuesday',
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        
        # Create URL for list availability
        self.list_url = reverse('list_availability', args=[self.hairdresser.id])
        
    def test_list_availability_success(self):
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)
        
        # Check first availability
        self.assertEqual(data['data'][0]['weekday'], 'monday')
        self.assertEqual(data['data'][0]['start_time'], '09:00:00')
        self.assertEqual(data['data'][0]['end_time'], '17:00:00')
        
        # Check second availability
        self.assertEqual(data['data'][1]['weekday'], 'tuesday')
        self.assertEqual(data['data'][1]['start_time'], '10:00:00')
        self.assertEqual(data['data'][1]['end_time'], '18:00:00')
        
    def test_list_availability_nonexistent_hairdresser(self):
        # Test with a non-existent hairdresser ID
        nonexistent_url = reverse('list_availability', args=[999])
        response = self.client.get(nonexistent_url)
        
        # The API should return an empty list rather than an error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Hairdresser not found')


class RemoveAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Create hairdresser user
        self.hairdresser_payload = {
            "email": "hairdresser@example.com",
            "first_name": "Hair",
            "last_name": "Dresser",
            "password": "password123",
            "phone": "+5592984502890",
            "complement": "casa",
            "neighborhood": "centro",
            "city": "manaus",
            "state": "AM",
            "address": "Salon Street",
            "number": "123",
            "postal_code": "12345678",
            "rating": 5,
            "role": "hairdresser",
            "cnpj": "12345678901212",
            "experience_years": 5,
            "resume": "Professional hairdresser",
            "preferences": json.dumps([]),
            'experience_time':'experience_time',
            'experiences':'experiences',
            'products':'products',
            'resume':'resume'
        }
        
        # Register hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Get hairdresser
        self.hairdresser = Hairdresser.objects.get(user__email="hairdresser@example.com")
        
        # Create availability
        self.availability = Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='monday',
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Create URL for remove availability
        self.remove_url = reverse('remove_availability', args=[self.availability.id])
        
    def test_remove_availability_success(self):
        response = self.client.delete(self.remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Availability.objects.count(), 0)
        
    def test_remove_nonexistent_availability(self):
        # Test with a non-existent availability ID
        nonexistent_url = reverse('remove_availability', args=[999])
        response = self.client.delete(nonexistent_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Availability.objects.count(), 1)  # Original availability still exists


class UpdateAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Create hairdresser user
        self.hairdresser_payload = {
            "email": "hairdresser@example.com",
            "first_name": "Hair",
            "last_name": "Dresser",
            "password": "password123",
            "phone": "+5592984502890",
            "complement": "casa",
            "neighborhood": "centro",
            "city": "manaus",
            "state": "AM",
            "address": "Salon Street",
            "number": "123",
            "postal_code": "12345678",
            "rating": 5,
            "role": "hairdresser",
            "cnpj": "12345678901212",
            "experience_years": 5,
            "resume": "Professional hairdresser",
            "preferences": json.dumps([]),
            'experience_time':'experience_time',
            'experiences':'experiences',
            'products':'products',
            'resume':'resume'
        }
        
        # Register hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        # Get hairdresser
        self.hairdresser = Hairdresser.objects.get(user__email="hairdresser@example.com")
        
        # Create availability
        self.availability = Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='monday',
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Create URL for update availability
        self.update_url = reverse('update_availability', args=[self.availability.id])
        
    def test_update_availability_all_fields(self):
        response = self.client.put(
            self.update_url,
            data=json.dumps({
                'weekday': 'wednesday',
                'start_time': '10:00:00',
                'end_time': '18:00:00'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh availability from database
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.weekday, 'wednesday')
        self.assertEqual(str(self.availability.start_time), '10:00:00')
        self.assertEqual(str(self.availability.end_time), '18:00:00')
        
    def test_update_availability_partial(self):
        response = self.client.put(
            self.update_url,
            data=json.dumps({
                'weekday': 'friday'
                # Not updating start_time and end_time
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh availability from database
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.weekday, 'friday')
        self.assertEqual(str(self.availability.start_time), '09:00:00')  # Should remain unchanged
        self.assertEqual(str(self.availability.end_time), '17:00:00')    # Should remain unchanged
        
    def test_update_nonexistent_availability(self):
        # Test with a non-existent availability ID
        nonexistent_url = reverse('update_availability', args=[999])
        response = self.client.put(
            nonexistent_url,
            data=json.dumps({
                'weekday': 'saturday',
                'start_time': '11:00:00',
                'end_time': '19:00:00'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Original availability should remain unchanged
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.weekday, 'monday')
        self.assertEqual(str(self.availability.start_time), '09:00:00')
        self.assertEqual(str(self.availability.end_time), '17:00:00')


class AvailabilityModelTest(TestCase):
    def setUp(self):
        # Create a user with hairdresser role
        self.user = User.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="testpassword",
            phone="1234567890",
            address="Test Street",
            number="42",
            postal_code="54321",
            role="HAIRDRESSER"
        )
        
        # Create hairdresser
        self.hairdresser = Hairdresser.objects.create(
            user=self.user,
            experience_years=3,
            resume="Test resume",
            cnpj="12345678901234"
        )
        
    def test_availability_model_creation(self):
        availability = Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='thursday',
            start_time=time(8, 30),
            end_time=time(16, 30)
        )
        
        self.assertEqual(availability.weekday, 'thursday')
        self.assertEqual(str(availability.start_time), '08:30:00')
        self.assertEqual(str(availability.end_time), '16:30:00')
        self.assertEqual(availability.hairdresser, self.hairdresser)
        
    def test_availability_model_relationships(self):
        # Create multiple availabilities for the same hairdresser
        Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='monday',
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='wednesday',
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        
        # Check that hairdresser has the expected number of availabilities
        self.assertEqual(self.hairdresser.availability.count(), 2)
        
        # Check that deleting the hairdresser also deletes the availabilities (cascade)
        hairdresser_id = self.hairdresser.id
        self.user.delete()  # This should also delete the hairdresser due to cascade
        self.assertEqual(Availability.objects.filter(hairdresser_id=hairdresser_id).count(), 0)

class UpdateMultipleAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Hairdresser payload
        self.hairdresser_payload = {
            "email": "rodrigosc615@gmail.com",
            "first_name": "Rodrigo Santos",
            "last_name": "o 12",
            "password": "senha123",
            "phone": "+5592984502890",
            "complement": "casa",
            "neighborhood": "centro",
            "city": "manaus",
            "state": "AM",
            "address": "rua francy assis",
            "number": "2229",
            "postal_code": "69050750",
            "rating": 5,
            "role": "hairdresser",
            "cnpj": "12345678901212",
            "experience_years": 4,
            "resume": "ele é legal e joga bem",
            "preferences": json.dumps([]),
            'experience_time':'experience_time',
            'experiences':'experiences',
            'products':'products',
            'resume':'resume'
        }
        
        # Register and login hairdresser
        self.client.post(
            self.register_url,
            data=self.hairdresser_payload,
        )
        
        login_payload = {
            'email': 'rodrigosc615@gmail.com',
            'password': 'senha123'
        }
        self.client.post(
            self.login_url,
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Get the hairdresser object
        self.hairdresser = Hairdresser.objects.get(user__email='rodrigosc615@gmail.com')
        
        # Create existing availabilities
        Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='monday',
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        Availability.objects.create(
            hairdresser=self.hairdresser,
            weekday='tuesday',
            start_time=time(10, 0),
            end_time=time(18, 0),
            break_start=time(12, 0),
            break_end=time(13, 0)
        )
        
        # URL for updating multiple availabilities
        self.update_multiple_url = reverse('update_multiple_availability', kwargs={'hairdresser_id': self.hairdresser.id})
    
    def test_update_multiple_availability_success(self):
        """Test successful update of multiple availabilities - should replace all existing ones"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'wednesday',
                    'start_time': '08:00:00',
                    'end_time': '16:00:00'
                },
                {
                    'weekday': 'thursday',
                    'start_time': '09:30:00',
                    'end_time': '17:30:00',
                    'break_start': '12:30:00',
                    'break_end': '13:30:00'
                },
                {
                    'weekday': 'friday',
                    'start_time': '10:00:00',
                    'end_time': '18:00:00'
                }
            ]
        }
        
        # Verify we start with 2 availabilities
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 2)
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'Multiple availabilities registered successfully')
        
        # Should have 3 new availabilities (old ones deleted)
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 3)
        
        # Verify old availabilities are gone
        self.assertFalse(Availability.objects.filter(hairdresser=self.hairdresser, weekday='monday').exists())
        self.assertFalse(Availability.objects.filter(hairdresser=self.hairdresser, weekday='tuesday').exists())
        
        # Verify new availabilities exist
        wednesday_availability = Availability.objects.get(hairdresser=self.hairdresser, weekday='wednesday')
        self.assertEqual(str(wednesday_availability.start_time), '08:00:00')
        self.assertEqual(str(wednesday_availability.end_time), '16:00:00')
        self.assertIsNone(wednesday_availability.break_start)
        self.assertIsNone(wednesday_availability.break_end)
        
        thursday_availability = Availability.objects.get(hairdresser=self.hairdresser, weekday='thursday')
        self.assertEqual(str(thursday_availability.start_time), '09:30:00')
        self.assertEqual(str(thursday_availability.end_time), '17:30:00')
        self.assertEqual(str(thursday_availability.break_start), '12:30:00')
        self.assertEqual(str(thursday_availability.break_end), '13:30:00')
        
        friday_availability = Availability.objects.get(hairdresser=self.hairdresser, weekday='friday')
        self.assertEqual(str(friday_availability.start_time), '10:00:00')
        self.assertEqual(str(friday_availability.end_time), '18:00:00')
    
    def test_update_multiple_availability_with_break_times(self):
        """Test update with break times only"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'saturday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00',
                    'break_start': '12:00:00',
                    'break_end': '13:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 1)
        
        availability = Availability.objects.get(hairdresser=self.hairdresser, weekday='saturday')
        self.assertEqual(str(availability.break_start), '12:00:00')
        self.assertEqual(str(availability.break_end), '13:00:00')
    
    def test_update_multiple_availability_without_break_times(self):
        """Test update without break times"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'sunday',
                    'start_time': '10:00:00',
                    'end_time': '16:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 1)
        
        availability = Availability.objects.get(hairdresser=self.hairdresser, weekday='sunday')
        self.assertIsNone(availability.break_start)
        self.assertIsNone(availability.break_end)
    
    def test_update_multiple_availability_missing_weekday(self):
        """Test update with missing weekday field"""
        payload = {
            'availabilities': [
                {
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('required fields is missing', data['error'])
    
    def test_update_multiple_availability_missing_start_time(self):
        """Test update with missing start_time field"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('required fields is missing', data['error'])
    
    def test_update_multiple_availability_missing_end_time(self):
        """Test update with missing end_time field"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('required fields is missing', data['error'])
    
    def test_update_multiple_availability_invalid_weekday(self):
        """Test update with invalid weekday"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'invalidday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('Invalid weekday', data['error'])
    
    def test_update_multiple_availability_nonexistent_hairdresser(self):
        """Test update for non-existent hairdresser"""
        non_existent_url = reverse('update_multiple_availability', kwargs={'hairdresser_id': 9999})
        
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                }
            ]
        }
        
        response = self.client.put(
            non_existent_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Hairdresser not found')
    
    def test_update_multiple_availability_empty_list(self):
        """Test update with empty availabilities list"""
        payload = {
            'availabilities': []
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # All existing availabilities should be deleted
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 0)
    
    def test_update_multiple_availability_duplicate_weekdays_in_payload(self):
        """Test update with duplicate weekdays in the same payload"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00'
                },
                {
                    'weekday': 'monday',
                    'start_time': '10:00:00',
                    'end_time': '18:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # This should fail because of duplicate weekdays
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('Availability already exists', data['error'])
    
    def test_update_multiple_availability_malformed_json(self):
        """Test update with malformed JSON"""
        response = self.client.put(
            self.update_multiple_url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_update_multiple_availability_missing_availabilities_key(self):
        """Test update with missing 'availabilities' key in payload"""
        payload = {
            'invalid_key': []
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_update_multiple_availability_partial_break_time(self):
        """Test update with only break_start or break_end (not both)"""
        payload = {
            'availabilities': [
                {
                    'weekday': 'monday',
                    'start_time': '09:00:00',
                    'end_time': '17:00:00',
                    'break_start': '12:00:00'
                    # Missing break_end
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should create availability without break times
        availability = Availability.objects.get(hairdresser=self.hairdresser, weekday='monday')
        self.assertIsNone(availability.break_start)
        self.assertIsNone(availability.break_end)
    
    def test_update_multiple_availability_replaces_all_existing(self):
        """Test that update replaces ALL existing availabilities, not just the ones with matching weekdays"""
        # Start with 2 existing availabilities (monday, tuesday)
        initial_count = Availability.objects.filter(hairdresser=self.hairdresser).count()
        self.assertEqual(initial_count, 2)
        
        # Update with completely different weekdays
        payload = {
            'availabilities': [
                {
                    'weekday': 'wednesday',
                    'start_time': '08:00:00',
                    'end_time': '16:00:00'
                },
                {
                    'weekday': 'saturday',
                    'start_time': '10:00:00',
                    'end_time': '14:00:00'
                }
            ]
        }
        
        response = self.client.put(
            self.update_multiple_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should have exactly 2 availabilities (the new ones)
        self.assertEqual(Availability.objects.filter(hairdresser=self.hairdresser).count(), 2)
        
        # Old availabilities should be gone
        self.assertFalse(Availability.objects.filter(hairdresser=self.hairdresser, weekday='monday').exists())
        self.assertFalse(Availability.objects.filter(hairdresser=self.hairdresser, weekday='tuesday').exists())
        
        # New availabilities should exist
        self.assertTrue(Availability.objects.filter(hairdresser=self.hairdresser, weekday='wednesday').exists())
        self.assertTrue(Availability.objects.filter(hairdresser=self.hairdresser, weekday='saturday').exists())