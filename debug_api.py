# debug_api.py
"""
Debug script to test F1 API endpoints and identify issues

Run this script to test all API endpoints and see what data is available.
This will help identify why session data isn't loading properly.

Usage: python debug_api.py
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.enhanced_data_service import EnhancedDataService
from services.api_client import ErgastAPIClient
import json

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_basic_endpoints():
    """Test basic F1 endpoints"""
    print("🔧 TESTING BASIC F1 ENDPOINTS")
    print("=" * 50)
    
    try:
        client = ErgastAPIClient()
        
        # Test current standings
        print("📊 Testing current standings...")
        standings_data = client.get_current_driver_standings()
        if standings_data and 'MRData' in standings_data:
            drivers_count = len(standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'])
            print(f"✅ Current standings: {drivers_count} drivers loaded")
        else:
            print("❌ Current standings: Failed")
        
        # Test current calendar
        print("📅 Testing current calendar...")
        calendar_data = client.get("current.json")
        if calendar_data and 'MRData' in calendar_data:
            races_count = len(calendar_data['MRData']['RaceTable']['Races'])
            print(f"✅ Current calendar: {races_count} races loaded")
        else:
            print("❌ Current calendar: Failed")
            
    except Exception as e:
        print(f"❌ Basic endpoints failed: {e}")
    
    print()

def test_session_endpoints():
    """Test session endpoints for recent races"""
    print("🏁 TESTING SESSION ENDPOINTS")
    print("=" * 50)
    
    # Test with recent seasons and races
    test_cases = [
        ("2024", "1", "Bahrain 2024"),
        ("2024", "5", "China 2024"),  # Sprint race
        ("2023", "1", "Bahrain 2023"),
        ("2025", "1", "First race 2025")
    ]
    
    client = ErgastAPIClient()
    
    for season, round_num, description in test_cases:
        print(f"🏎️ Testing {description} (Season {season}, Round {round_num})")
        
        # Test each session type
        session_tests = [
            ("Qualifying", f"{season}/{round_num}/qualifying.json"),
            ("Race Results", f"{season}/{round_num}/results.json"),
            ("Practice 1", f"{season}/{round_num}/practice/1.json"),
            ("Practice 2", f"{season}/{round_num}/practice/2.json"),
            ("Practice 3", f"{season}/{round_num}/practice/3.json"),
            ("Sprint", f"{season}/{round_num}/sprint.json")
        ]
        
        for session_name, endpoint in session_tests:
            try:
                data = client.get(endpoint)
                if data and 'MRData' in data:
                    race_table = data['MRData']['RaceTable']
                    if 'Races' in race_table and race_table['Races']:
                        race_data = race_table['Races'][0]
                        
                        # Check what results are available
                        results_keys = [key for key in race_data.keys() if 'Results' in key or 'Result' in key]
                        if results_keys:
                            results_data = race_data[results_keys[0]]
                            print(f"  ✅ {session_name}: {len(results_data)} results")
                        else:
                            print(f"  ⚠️  {session_name}: Data structure available but no results")
                            print(f"      Available keys: {list(race_data.keys())}")
                    else:
                        print(f"  ⚠️  {session_name}: No race data")
                else:
                    print(f"  ❌ {session_name}: No valid response")
            except Exception as e:
                print(f"  ❌ {session_name}: {str(e)}")
        
        print()

def test_driver_career_data():
    """Test career data loading for a sample driver"""
    print("👤 TESTING DRIVER CAREER DATA")
    print("=" * 50)
    
    # Test with well-known drivers
    test_drivers = [
        ("hamilton", "Lewis Hamilton"),
        ("verstappen", "Max Verstappen"),
        ("leclerc", "Charles Leclerc")
    ]
    
    client = ErgastAPIClient()
    
    for driver_id, driver_name in test_drivers:
        print(f"🏎️ Testing career data for {driver_name} ({driver_id})")
        
        try:
            # Test seasons endpoint
            seasons_data = client.get(f"drivers/{driver_id}/seasons.json?limit=100")
            if seasons_data and 'MRData' in seasons_data:
                seasons = seasons_data['MRData']['SeasonTable'].get('Seasons', [])
                print(f"  ✅ Seasons: {len(seasons)} seasons found")
                
                if seasons:
                    latest_season = seasons[-1]['season']
                    print(f"      Latest season: {latest_season}")
                    
                    # Test getting standings for latest season
                    standings_data = client.get(f"{latest_season}/drivers/{driver_id}/driverStandings.json")
                    if standings_data and 'MRData' in standings_data:
                        standings = standings_data['MRData']['StandingsTable'].get('StandingsLists', [])
                        if standings:
                            driver_standing = standings[0]['DriverStandings'][0]
                            points = driver_standing.get('points', 0)
                            wins = driver_standing.get('wins', 0)
                            print(f"      {latest_season} stats: {points} points, {wins} wins")
                        else:
                            print(f"      ❌ No standings data for {latest_season}")
            else:
                print(f"  ❌ No seasons data found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()

def test_enhanced_data_service():
    """Test the enhanced data service"""
    print("🚀 TESTING ENHANCED DATA SERVICE")
    print("=" * 50)
    
    try:
        service = EnhancedDataService()
        
        # Test session endpoints status
        print("📡 Testing session endpoints availability...")
        endpoints_status = service.test_session_endpoints("2024", "1")
        
        for endpoint, status in endpoints_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {endpoint}")
        
        print()
        
        # Test standings loading
        print("📊 Testing standings loading...")
        standings = service.get_current_f1_standings()
        print(f"✅ Loaded {len(standings)} drivers")
        
        # Show first 3 drivers
        for i, standing in enumerate(standings[:3]):
            print(f"  {i+1}. {standing.driver.full_name} - {int(standing.points)} pts")
        
        print()
        
    except Exception as e:
        print(f"❌ Enhanced data service failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🏁 F1 API DEBUG TOOL")
    print("=" * 50)
    print("This tool will test all F1 API endpoints to identify issues.")
    print()
    
    # Run tests
    test_basic_endpoints()
    test_session_endpoints()
    test_driver_career_data()
    test_enhanced_data_service()
    
    print("🏁 DEBUG COMPLETE")
    print("=" * 50)
    print("If you see ❌ for session endpoints, those data types are not")
    print("available in the API. Only ✅ endpoints will work in the app.")
    print()
    print("Common findings:")
    print("- Qualifying and Race data usually work")
    print("- Practice sessions often not available")
    print("- Sprint data only available for Sprint weekends")
    print("- Future race data (2025) might not be available yet")

if __name__ == "__main__":
    main()