import requests
import numpy as np
import math
from datetime import datetime, timedelta
import pandas as pd

class MandiAPI:
    def __init__(self):
       self.base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
       self.api_key = "579b464db66ec23bdd000001a13a8ff7df7842db6af8e9322f1c3560"
       self.location_api_key = "AIzaSyCo9j3bas4HmenXcrv-XORXTHb-5v73GTA" 
       self.weather_api_key = "3f010e52c461f5f74f7afa9b54c03265"

    def get_api_url(self, state, limit=1000):
        return f"{self.base_url}?api-key={self.api_key}&format=json&limit={limit}&filters[state.keyword]={state}"
    
    def get_current_prices(self, state, crop, predictor):
        try:
            url = self.get_api_url(state)
            response = requests.get(url, timeout=15)
            response.raise_for_status() 
            data = response.json()
            parsed_data = self.parse_api_data(data, crop)
            if parsed_data:
                return parsed_data
            else:
                return self._create_fallback_price(state, crop, predictor)
        except Exception:
            return self._create_fallback_price(state, crop, predictor)

    def parse_api_data(self, data, crop):
        records = data.get('records', [])
        if not records: return None
        
        price_data = {}
        markets_found = 0
        for record in records:
            if crop.lower() in record.get('commodity', '').lower():
                market = record.get('market', 'Unknown Market').strip()
                if market not in price_data:
                    try:
                        price_data[market] = {
                            'min_price': int(record.get('min_price', 0)),
                            'max_price': int(record.get('max_price', 0)),
                            'modal_price': int(record.get('modal_price', 0)),
                        }
                        markets_found += 1
                        if markets_found >= 3: break 
                    except (ValueError, TypeError): continue
        return price_data if price_data else None

    def _create_fallback_price(self, state, crop, predictor):
        latest_price = predictor.get_latest_price(state, crop)
        if latest_price:
            return {
                'fallback': True,
                'data': {
                    "Estimated Market": {
                        'modal_price': int(latest_price),
                        'min_price': int(latest_price * 0.95),
                        'max_price': int(latest_price * 1.05)
                    }
                }
            }
        return None

    def get_weekly_historical_data(self, state, crop):
        """
        Last 7 days  realistic historical data create
        """
        try:
            
            current_price_data = self.get_current_prices(state, crop, None)
            current_price = 2000  
            
            if current_price_data:
                if 'fallback' in current_price_data:
                    current_price = current_price_data['data']['Estimated Market']['modal_price']
                else:
                    
                    for market, data in current_price_data.items():
                        current_price = data['modal_price']
                        break
            
            
            dates = []
            for i in range(6, -1, -1):
                date = datetime.now() - timedelta(days=i)
                dates.append(date.strftime('%Y-%m-%d'))
            
            
            prices = self._generate_realistic_prices(current_price)
            
            return {
                'dates': dates,
                'prices': prices,
                'current_price': current_price
            }
            
        except Exception as e:
            print(f"   ⚠ Error creating historical data: {e}")
            return self._create_sample_historical_data()

    def _generate_realistic_prices(self, current_price):
        """
        Realistic price trend generate 
        """
        prices = []
        base_price = current_price * 0.85 
        
        for i in range(7):
            if i == 6: 
                price = current_price
            else:
               
                progress = (i + 1) / 7
                target_price = base_price + (current_price - base_price) * progress
                
               
                variation = np.random.uniform(-0.03, 0.03)
                price = target_price * (1 + variation)
                
                
                price = max(price, base_price * 0.95)
            
            prices.append(int(price))
        
        return prices

    def _create_sample_historical_data(self):
        """
        Sample historical data if not founded
        """
        dates = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        
        
        base_price = 2100
        prices = []
        
        for i in range(7):
            if i == 6:  
                price = base_price
            else:
                
                variation = np.random.uniform(-0.04, 0.04)
                price = base_price * (1 + variation)
            prices.append(int(price))
        
        return {
            'dates': dates,
            'prices': prices,
            'current_price': base_price
        }

    def get_state_from_coords(self, lat, lng):
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lng}",
                'key': self.location_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                for component in data['results'][0]['address_components']:
                    if 'administrative_area_level_1' in component['types']:
                        state_name = component['long_name']
                        return state_name
            return None
        except Exception as e:
            print(f"   ⚠️ Error in reverse geocoding: {e}")
            return None

    def get_weather_data_for_state(self, state):
        try:
            state_coordinates = {
                'Punjab': (30.7333, 76.7794),
                'Haryana': (28.6139, 77.2090),
                'Uttar Pradesh': (26.8467, 80.9462),
                'Rajasthan': (26.9124, 75.7873),
                'Maharashtra': (19.0760, 72.8777),
                'Madhya Pradesh': (23.2599, 77.4126),
                'Karnataka': (12.9716, 77.5946),
                'West Bengal': (22.5726, 88.3639),
                'Gujarat': (23.0225, 72.5714),
                'Bihar': (25.5941, 85.1376),
                'Andhra Pradesh': (16.5062, 80.6480),
                'Telangana': (17.3850, 78.4867),
            }
            
            lat, lng = state_coordinates.get(state, (29.6857, 76.9905))
            
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={self.weather_api_key}&units=metric"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'rainfall': data.get('rain', {}).get('1h', 0),
                    'description': data['weather'][0]['description']
                }
            else:
                return {
                    'temperature': 25.0,
                    'humidity': 60.0,
                    'rainfall': 0.0,
                    'description': 'Weather data unavailable'
                }
                
        except Exception:
            return {
                'temperature': 25.0,
                'humidity': 60.0,
                'rainfall': 0.0,
                'description': 'Weather data unavailable'
            }