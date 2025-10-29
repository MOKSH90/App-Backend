from Market.predictor.mandi_api import MandiAPI
from Market.predictor.price_predictor import PricePredictor
import matplotlib.pyplot as plt
import pandas as pd

class FarmerPriceTracker:
    def __init__(self):
        print("Initializing the application...")
        self.predictor = PricePredictor()
        self.api = MandiAPI()
        
        self.available_states = self.predictor.get_available_states()
        self.crops = self.predictor.get_available_crops()

    def get_location_data(self):
        while True:
            print("\n" + "="*60)
            print("   📍 Please enter your coordinates (Latitude and Longitude)")
            try:
                lat_str = input("      Enter Latitude (e.g., 28.6139): ").strip()
                lng_str = input("      Enter Longitude (e.g., 77.2090): ").strip()
                
                if not lat_str or not lng_str:
                    print("   ⚠️ No input provided. Using Karnal (29.6857, 76.9905) as default.")
                    lat = 29.6857
                    lng = 76.9905
                else:
                    lat = float(lat_str)
                    lng = float(lng_str)
                
                print(f"\n   🌍 Fetching state for coordinates {lat}, {lng}...")
                state = self.api.get_state_from_coords(lat, lng)
                
                if state and state in self.available_states:
                    print(f"   ✅ Location found: {state}")
                    return state
                elif state:
                    print(f"   ⚠️ Found state '{state}', but we do not have prediction data for it.")
                    print("   Please enter coordinates for one of the supported states:")
                    print(f"   {', '.join(self.available_states)}")
                else:
                    print("   ⚠️ Could not find a state for these coordinates. Please try again.")
                    
            except (ValueError, TypeError):
                print("   ⚠️ Invalid number. Please enter coordinates like: 28.6139")
            except Exception as e:
                print(f"   ⚠️ An error occurred: {e}")

    def select_crop(self):
        print("\n--- Available Crops ---")
        for i in range(0, len(self.crops), 2):
            col1 = f"{i+1}. {self.crops[i]}"
            col2 = ""
            if i + 1 < len(self.crops):
                col2 = f"{i+2}. {self.crops[i+1]}"
            print(f"{col1:<25} {col2}")

        while True:
            try:
                choice = int(input("\nSelect a crop (enter number): "))
                if 1 <= choice <= len(self.crops):
                    return self.crops[choice - 1]
                else:
                    print(" Invalid number! Please try again.")
            except (ValueError, KeyboardInterrupt):
                print(" Please enter a valid number!")

    def display_full_report(self, state, crop):
        print("\n" + "="*60)
        print(f" FARMER'S REPORT FOR: {crop.upper()} in {state.upper()} ")
        print("="*60)

        print("\n📊 Fetching Current Market Prices...")
        price_data = self.api.get_current_prices(state, crop, self.predictor)
        self.display_price_info(price_data, crop)

        print("\n🤖 Generating Price Prediction...")
        prediction_data = self.predictor.ml_price_prediction(state, crop)
        self.display_prediction(prediction_data)

        # print("\n📈 Generating Price Trend Chart...")
        # self.display_line_chart(prediction_data, crop, state)
        
        print("\n" + "="*60)

    def display_price_info(self, price_data, crop):
        print("\n--- CURRENT PRICES ---")
        if price_data and 'fallback' in price_data:
            for market, data in price_data['data'].items():
                print(f"\n   Market: {market}:")
                print(f"     - Min Price:   ₹{data.get('min_price', 'N/A')}/quintal")
                print(f"     - Max Price:   ₹{data.get('max_price', 'N/A')}/quintal")
                print(f"     - model Price: ₹{data.get('model_price', 'N/A')}/quintal")
        elif price_data:
            for market, data in price_data.items():
                print(f"\n   Market: {market}:")
                print(f"     - Min Price:   ₹{data.get('min_price', 'N/A')}/quintal")
                print(f"     - Max Price:   ₹{data.get('max_price', 'N/A')}/quintal")
                print(f"     - model Price: ₹{data.get('model_price', 'N/A')}/quintal")
        else:
            print(f"   No current LIVE data available for '{crop}'.")

    def display_prediction(self, prediction_data):
        print("\n--- PRICE PREDICTION ---")
        
        if 'error' in prediction_data:
            print(f"   {prediction_data['error']}")
            return
            
        print(f"   Current Price: ₹{prediction_data['current_price']:,.2f}/quintal")
        print(f"   Market Trend: {prediction_data['trend']}")
        print(f"   Confidence: {prediction_data['confidence']}%")
        print(f"   Weather Impact: {prediction_data['weather_impact']}")
        
        print(f"\n   📈 Next 4 Weeks Forecast:")
        for week, data in prediction_data['weekly_forecast'].items():
            change_percent = data['change_percent']
            arrow = "↑" if change_percent > 0 else "↓" if change_percent < 0 else "→"
            print(f"       {week}: ₹{data['price']:,.2f} {arrow} ({change_percent:+.1f}%)")
        
        print(f"\n   💡 Recommendation: {prediction_data['recommendation']}")

    # def display_line_chart(self, prediction_data, crop, state):
    #     if 'error' in prediction_data:
    #         return
            
    #     try:
           
    #         plt.figure(figsize=(12, 6))
            
    #         weeks = ['Current'] + list(prediction_data['weekly_forecast'].keys())
    #         prices = [prediction_data['current_price']] + [data['price'] for data in prediction_data['weekly_forecast'].values()]
    #         changes = [0] + [data['change_percent'] for data in prediction_data['weekly_forecast'].values()]
            
    #         plt.plot(weeks, prices, marker='o', linewidth=3, markersize=8, color='#2E8B57')
    #         plt.fill_between(weeks, prices, alpha=0.2, color='#2E8B57')
            
    #         plt.title(f'{crop} Price Forecast - {state}', fontsize=16, fontweight='bold', pad=20)
    #         plt.xlabel('Timeline', fontsize=12)
    #         plt.ylabel('Price (₹/quintal)', fontsize=12)
    #         plt.grid(True, alpha=0.3)
            
           
    #         for i, (week, price, change) in enumerate(zip(weeks, prices, changes)):
    #             color = 'green' if change >= 0 else 'red' if change < 0 else 'blue'
    #             plt.annotate(f'₹{price:,.0f}\n({change:+.1f}%)', 
    #                        (week, price), 
    #                        textcoords="offset points", 
    #                        xytext=(0,15), 
    #                        ha='center', 
    #                        fontsize=10,
    #                        color=color,
    #                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))
            
    #         plt.tight_layout()
    #         plt.show()
            
    #     except Exception as e:
    #         print(f"   Could not display chart: {e}")

    def run(self):
        print("="*60)
        print("🌾 WELCOME TO THE FARMER PRICE TRACKER 🌾")
        
        while True:
            state = self.get_location_data() 
            if not state:
                continue
            
            crop = self.select_crop()
            
            self.display_full_report(state, crop)

            while True:
                another_search = input("\nDo you want to search for another crop? (yes/no): ").lower().strip()
                if another_search in ["yes", "y", "no", "n"]:
                    break
                else:
                    print(" Invalid input. Please enter 'yes' or 'no'.")
            
            if another_search in ["no", "n"]:
                print("\n Thank you for using the Farmer Price Tracker!")
                break

if __name__ == "__main__":
    try:
        app = FarmerPriceTracker()
        app.run()
    except KeyboardInterrupt:
        print("\n Program closed by user.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {e}")