from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import Country, Location  # Import your models
from .serializers import CountrySerializer




from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import Country, Location  # Import your models
from .serializers import CountrySerializer



from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import Country, Location  # Import your models
from .serializers import CountrySerializer

class HomePageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test data (fixtures) for the tests
        Country.objects.create(name='Country1')
        Location.objects.create(name='Location1', country_id=1, latitude=0.0,longitude=0.0)

    def setUp(self):
        self.client = Client()

    @patch('requests.post')  # Mock the requests.post method
    @patch('geo_search.serializers.CountrySerializer')  # Mock the CountrySerializer
    def test_homepage_view(self, mock_serializer, mock_post):
        # Mock the response from the external API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'search_results': [{'result1': 'data1'}, {'result2': 'data2'}]
        }

        # Mock the serializer's return value
        mock_serializer.return_value = 'MockedSerializer'

        # Simulate a POST request to the homepage view
        response = self.client.post(reverse('home'), {
            'countries': [1],  # Use the IDs of the test data created in setUpTestData
            'location': [1],
            'search': 'search_query',
            'num_results': 10
        })

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the search results are present in the response context
        self.assertIn('search_results', response.context)

        # Check that the mocked serializer was used
        mock_serializer.assert_called_once_with(Country.objects.all(), many=True)

        # Check that the serializer variable in the context matches the mocked serializer
        self.assertEqual(response.context['serializer'], 'MockedSerializer')

        # Check if the search results match the expected data from the mocked API response
        expected_results = [{'city': 'Location1', 'results': [{'result1': 'data1'}, {'result2': 'data2'}]}]
        self.assertEqual(response.context['search_results'], expected_results)

        # Check that the mocked API request was made with the correct data
        mock_post.assert_called_once_with(
            'http://127.0.0.1:8080/api/geo_location/',
            data={
                'city': 'Location1',
                'search_content': 'search_query',
                'num_results': 10
            }
        )
