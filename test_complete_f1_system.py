# test_complete_f1_system.py
"""
Complete F1 system test and debug script

This script tests all F1 API endpoints, career statistics loading,
and session data retrieval to ensure everything works correctly.

Usage: python test_complete_f1_system.py
"""

import sys
import logging
from pathlib import Path
import asyncio
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.enhanced_data_service import EnhancedDataService, OpenF1Client
from services.api_client import ErgastAPIClient
from models.driver import DriverStanding

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/f1_system_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_basic_api_connectivity():
    """Test basic API connectivity and endpoints"""
    print("🔧 TESTING BASIC API CONNECTIVITY")
    print("=" * 60)
    
    try:
        client = ErgastAPIClient()
        
        # Test 1: Current standings
        print("📊 Testing current standings...")
        standings_data = client.get_current_driver_standings()
        if standings_data and 'MRData' in standings_data:
            drivers_count = len(standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'])
            print(f"✅ Current standings: {drivers_count} drivers loaded")
            
            # Show top 3 drivers
            for i, driver_data in enumerate(standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'][:3]):
                driver_name = f"{driver_data['Driver']['givenName']} {driver_data['Driver']['familyName']}"
                points = driver_data['points']
                print(f"   {i+1}. {driver_name} - {points} pts")
        else:
            print("❌ Current standings: Failed")
        
        # Test 2: Current calendar
        print("\n📅 Testing current calendar...")
        calendar_data = client.get("2025.json")
        if calendar_data and 'MRData' in calendar_data:
            races_count = len(calendar_data['MRData']['RaceTable']['Races'])
            print(f"✅ Current calendar: {races_count} races loaded")
            
            # Show first 3 races
            for i, race in enumerate(calendar_data['MRData']['RaceTable']['Races'][:3]):
                race_name = race['raceName']
                date = race['date']
                print(f"   {i+1}. {race_name} - {date}")
        else:
            print("❌ Current calendar: Failed")
            
        # Test 3: OpenF1 connectivity
        print("\n🔗 Testing OpenF1 connectivity...")
        openf1_client = OpenF1Client()
        sessions = openf1_client.get_sessions(2025)
        if sessions:
            print(f"✅ OpenF1 connected: {len(sessions)} sessions available")
        else:
            print("⚠️ OpenF1: No sessions data (may be expected for 2025)")
            
    except Exception as e:
        print(f"❌ Basic API test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_all_2025_endpoints():
    """Test all available 2025 F1 endpoints"""
    print("🏁 TESTING ALL 2025 F1 ENDPOINTS")
    print("=" * 60)
    
    client = ErgastAPIClient()
    
    # Define all endpoints to test
    endpoints_to_test = [
        ("Races", "2025.json"),
        ("All Results", "2025/results.json"),
        ("All Qualifying", "2025/qualifying.json"), 
        ("All Sprint", "2025/sprint.json"),
        ("Driver Standings", "2025/driverStandings.json"),
        ("Constructor Standings", "2025/constructorStandings.json"),
    ]
    
    for endpoint_name, endpoint_url in endpoints_to_test:
        try:
            print(f"🔍 Testing {endpoint_name} ({endpoint_url})...")
            data = client.get(endpoint_url)
            
            if data and 'MRData' in data:
                # Different endpoints have different structures
                if 'RaceTable' in data['MRData']:
                    races = data['MRData']['RaceTable'].get('Races', [])
                    print(f"✅ {endpoint_name}: {len(races)} races with data")
                    
                    # Show sample data
                    if races:
                        sample_race = races[0]
                        race_name = sample_race.get('raceName', 'Unknown')
                        round_num = sample_race.get('round', 'Unknown')
                        print(f"   Sample: Round {round_num} - {race_name}")
                        
                        # Check what data is available in the race
                        data_types = []
                        if 'Results' in sample_race:
                            data_types.append(f"Results ({len(sample_race['Results'])})")
                        if 'QualifyingResults' in sample_race:
                            data_types.append(f"Qualifying ({len(sample_race['QualifyingResults'])})")
                        if 'SprintResults' in sample_race:
                            data_types.append(f"Sprint ({len(sample_race['SprintResults'])})")
                        if 'PitStops' in sample_race:
                            data_types.append(f"Pit Stops ({len(sample_race['PitStops'])})")
                        if 'Laps' in sample_race:
                            data_types.append(f"Laps ({len(sample_race['Laps'])})")
                        
                        if data_types:
                            print(f"   Available data: {', '.join(data_types)}")
                        else:
                            print(f"   Available keys: {list(sample_race.keys())}")
                
                elif 'StandingsTable' in data['MRData']:
                    standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
                    if standings_lists:
                        if 'DriverStandings' in standings_lists[0]:
                            standings = standings_lists[0]['DriverStandings']
                            print(f"✅ {endpoint_name}: {len(standings)} drivers")
                        elif 'ConstructorStandings' in standings_lists[0]:
                            standings = standings_lists[0]['ConstructorStandings']
                            print(f"✅ {endpoint_name}: {len(standings)} constructors")
                    else:
                        print(f"⚠️ {endpoint_name}: No standings data")
                        
            else:
                print(f"❌ {endpoint_name}: No valid data")
                
        except Exception as e:
            print(f"❌ {endpoint_name}: Error - {str(e)}")
    
    print()

def test_specific_race_sessions():
    """Test specific race session endpoints"""
    print("🏎️ TESTING SPECIFIC RACE SESSION ENDPOINTS")
    print("=" * 60)
    
    client = ErgastAPIClient()
    
    # Test with different rounds (some may have data, others may not)
    test_rounds = [
        ("1", "Round 1 (First race)"),
        ("2", "Round 2 (Second race)"),
        ("5", "Round 5 (Mid season)"),
    ]
    
    for round_num, description in test_rounds:
        print(f"🏁 Testing {description}")
        
        # Session types to test
        session_endpoints = [
            ("Qualifying", f"2025/{round_num}/qualifying.json"),
            ("Race Results", f"2025/{round_num}/results.json"),
            ("Sprint", f"2025/{round_num}/sprint.json"),
            ("Pit Stops", f"2025/{round_num}/pitstops.json"),
            ("Lap Times", f"2025/{round_num}/laps.json"),
        ]
        
        for session_name, endpoint in session_endpoints:
            try:
                data = client.get(endpoint)
                if data and 'MRData' in data and 'RaceTable' in data['MRData']:
                    races = data['MRData']['RaceTable'].get('Races', [])
                    if races:
                        race_data = races[0]
                        
                        # Count results for different session types
                        if session_name == "Qualifying" and 'QualifyingResults' in race_data:
                            results = race_data['QualifyingResults']
                            print(f"  ✅ {session_name}: {len(results)} results")
                        elif session_name == "Race Results" and 'Results' in race_data:
                            results = race_data['Results']
                            print(f"  ✅ {session_name}: {len(results)} results")
                        elif session_name == "Sprint" and 'SprintResults' in race_data:
                            results = race_data['SprintResults']
                            print(f"  ✅ {session_name}: {len(results)} results")
                        elif session_name == "Pit Stops" and 'PitStops' in race_data:
                            results = race_data['PitStops']
                            print(f"  ✅ {session_name}: {len(results)} pit stops")
                        elif session_name == "Lap Times" and 'Laps' in race_data:
                            results = race_data['Laps']
                            total_timings = sum(len(lap.get('Timings', [])) for lap in results)
                            print(f"  ✅ {session_name}: {len(results)} laps, {total_timings} total timings")
                        else:
                            print(f"  ⚠️ {session_name}: No data (expected for future races)")
                    else:
                        print(f"  ⚠️ {session_name}: No race data")
                else:
                    print(f"  ⚠️ {session_name}: No valid response")
                    
            except Exception as e:
                print(f"  ❌ {session_name}: Error - {str(e)}")
        
        print()

def test_career_statistics():
    """Test career statistics loading for known drivers"""
    print("👤 TESTING CAREER STATISTICS")
    print("=" * 60)
    
    # Test with well-known current drivers
    test_drivers = [
        ("hamilton", "Lewis Hamilton"),
        ("verstappen", "Max Verstappen"),
        ("leclerc", "Charles Leclerc"),
        ("russell", "George Russell"),
        ("sainz", "Carlos Sainz"),
    ]
    
    client = ErgastAPIClient()
    
    for driver_id, driver_name in test_drivers:
        print(f"🏎️ Testing career stats for {driver_name} ({driver_id})")
        
        try:
            # Test seasons endpoint
            seasons_data = client.get(f"drivers/{driver_id}/seasons.json?limit=100")
            if seasons_data and 'MRData' in seasons_data:
                seasons = seasons_data['MRData']['SeasonTable'].get('Seasons', [])
                print(f"  ✅ Seasons: {len(seasons)} seasons found")
                
                if seasons:
                    first_season = seasons[0]['season']
                    latest_season = seasons[-1]['season']
                    print(f"      Career span: {first_season} - {latest_season}")
                    
                    # Test getting standings for latest season
                    standings_data = client.get(f"{latest_season}/drivers/{driver_id}/driverStandings.json")
                    if standings_data and 'MRData' in standings_data:
                        standings_lists = standings_data['MRData']['StandingsTable'].get('StandingsLists', [])
                        if standings_lists and standings_lists[0].get('DriverStandings'):
                            driver_standing = standings_lists[0]['DriverStandings'][0]
                            points = driver_standing.get('points', 0)
                            wins = driver_standing.get('wins', 0)
                            position = driver_standing.get('position', 'N/A')
                            print(f"      {latest_season} stats: P{position}, {points} points, {wins} wins")
                        else:
                            print(f"      ⚠️ No standings data for {latest_season}")
                    
                    # Test race results for a sample season
                    sample_season = latest_season
                    results_data = client.get(f"{sample_season}/drivers/{driver_id}/results.json?limit=100")
                    if results_data and 'MRData' in results_data:
                        races = results_data['MRData']['RaceTable'].get('Races', [])
                        total_races = len(races)
                        podiums = 0
                        for race in races:
                            for result in race.get('Results', []):
                                position = result.get('position')
                                if position and position.isdigit() and int(position) <= 3:
                                    podiums += 1
                        print(f"      {sample_season} details: {total_races} races, {podiums} podiums")
                    
            else:
                print(f"  ❌ No seasons data found for {driver_id}")
                
        except Exception as e:
            print(f"  ❌ Error loading data for {driver_id}: {str(e)}")
        
        print()

def test_enhanced_data_service():
    """Test the complete enhanced data service"""
    print("🚀 TESTING ENHANCED DATA SERVICE")
    print("=" * 60)
    
    try:
        service = EnhancedDataService()
        
        # Test 1: Data availability check
        print("📡 Testing data availability check...")
        availability = service.check_data_availability("2025")
        
        print("Data availability status:")
        for endpoint, status in availability.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {endpoint}")
        
        print()
        
        # Test 2: Current standings
        print("📊 Testing enhanced standings loading...")
        standings = service.get_current_f1_standings()
        print(f"✅ Loaded {len(standings)} drivers")
        
        # Show top 5 drivers
        for i, standing in enumerate(standings[:5]):
            print(f"  {i+1}. {standing.driver.full_name} ({standing.driver.code}) - {int(standing.points)} pts")
        
        print()
        
        # Test 3: Season calendar
        print("📅 Testing enhanced calendar loading...")
        calendar = service.get_season_race_calendar("2025")
        print(f"✅ Loaded {len(calendar)} races")
        
        # Show first 5 races
        for i, race in enumerate(calendar[:5]):
            podium_info = f" (Podium: {', '.join(race.podium[:3])})" if race.podium else " (No results yet)"
            print(f"  {race.round}. {race.race_name} - {race.date}{podium_info}")
        
        print()
        
        # Test 4: Complete 2025 data
        print("🏁 Testing complete 2025 season data...")
        season_data = service.get_all_2025_data()
        
        if season_data:
            print("Complete season data loaded:")
            if 'races' in season_data:
                print(f"  📅 Races: {len(season_data['races'])}")
            if 'results' in season_data:
                races_with_results = len([r for r in season_data['results'] if r.get('Results')])
                print(f"  🏁 Race results: {races_with_results} races completed")
            if 'qualifying' in season_data:
                races_with_qualifying = len([r for r in season_data['qualifying'] if r.get('QualifyingResults')])
                print(f"  ⏱️ Qualifying results: {races_with_qualifying} sessions")
            if 'sprint' in season_data:
                races_with_sprint = len([r for r in season_data['sprint'] if r.get('SprintResults')])
                print(f"  ⚡ Sprint results: {races_with_sprint} sprint races")
        else:
            print("❌ No complete season data available")
        
        print()
        
    except Exception as e:
        print(f"❌ Enhanced data service test failed: {e}")
        import traceback
        traceback.print_exc()

def test_session_data_loader():
    """Test the complete session data loader"""
    print("📊 TESTING COMPLETE SESSION DATA LOADER")
    print("=" * 60)
    
    try:
        service = EnhancedDataService()
        
        # Test with Round 1 (most likely to have data)
        print("🏁 Testing session data loader for Round 1...")
        
        # This would normally be run in a separate thread, but for testing we'll check the endpoints directly
        client = ErgastAPIClient()
        openf1_client = OpenF1Client()
        
        # Test each endpoint that the loader would use
        session_endpoints = [
            ("Qualifying", "2025/1/qualifying.json"),
            ("Race", "2025/1/results.json"),
            ("Sprint", "2025/1/sprint.json"),
            ("Pit Stops", "2025/1/pitstops.json"),
            ("Lap Times", "2025/1/laps.json"),
        ]
        
        session_results = {}
        
        for session_name, endpoint in session_endpoints:
            try:
                data = client.get(endpoint)
                if data and 'MRData' in data and 'RaceTable' in data['MRData']:
                    races = data['MRData']['RaceTable'].get('Races', [])
                    if races:
                        race_data = races[0]
                        
                        # Extract results based on session type
                        if session_name == "Qualifying" and 'QualifyingResults' in race_data:
                            results = race_data['QualifyingResults']
                            session_results[session_name] = results
                            print(f"  ✅ {session_name}: {len(results)} results")
                        elif session_name == "Race" and 'Results' in race_data:
                            results = race_data['Results']
                            session_results[session_name] = results
                            print(f"  ✅ {session_name}: {len(results)} results")
                        elif session_name == "Sprint" and 'SprintResults' in race_data:
                            results = race_data['SprintResults']
                            session_results[session_name] = results
                            print(f"  ✅ {session_name}: {len(results)} results")
                        elif session_name == "Pit Stops" and 'PitStops' in race_data:
                            results = race_data['PitStops']
                            session_results[session_name] = results
                            print(f"  ✅ {session_name}: {len(results)} pit stops")
                            
                            # Show sample pit stop
                            if results:
                                sample_stop = results[0]
                                driver_info = sample_stop.get('driver', {})
                                driver_name = f"{driver_info.get('givenName', '')} {driver_info.get('familyName', '')}"
                                lap = sample_stop.get('lap', 'N/A')
                                duration = sample_stop.get('duration', 'N/A')
                                print(f"      Sample: {driver_name} - Lap {lap} - {duration}s")
                                
                        elif session_name == "Lap Times" and 'Laps' in race_data:
                            laps = race_data['Laps']
                            session_results[session_name] = laps
                            total_timings = sum(len(lap.get('Timings', [])) for lap in laps)
                            print(f"  ✅ {session_name}: {len(laps)} laps, {total_timings} total timings")
                            
                            # Show sample lap timing
                            if laps and laps[0].get('Timings'):
                                sample_lap = laps[0]
                                sample_timing = sample_lap['Timings'][0]
                                lap_num = sample_lap.get('number', 'N/A')
                                driver_id = sample_timing.get('driverId', 'N/A')
                                lap_time = sample_timing.get('time', 'N/A')
                                print(f"      Sample: Lap {lap_num} - {driver_id} - {lap_time}")
                        else:
                            print(f"  ⚠️ {session_name}: No data available")
                    else:
                        print(f"  ⚠️ {session_name}: No race data")
                else:
                    print(f"  ⚠️ {session_name}: No valid response")
                    
            except Exception as e:
                print(f"  ❌ {session_name}: Error - {str(e)}")
        
        # Test OpenF1 connectivity
        print("\n🔗 Testing OpenF1 integration...")
        try:
            sessions = openf1_client.get_sessions(2025)
            if sessions:
                print(f"✅ OpenF1: {len(sessions)} sessions available")
                
                # Show sample session
                if sessions:
                    sample_session = sessions[0]
                    session_name = sample_session.get('session_name', 'Unknown')
                    date = sample_session.get('date_start', 'Unknown')
                    print(f"   Sample: {session_name} - {date}")
            else:
                print("⚠️ OpenF1: No sessions data (expected for future seasons)")
                
        except Exception as e:
            print(f"❌ OpenF1: Error - {str(e)}")
        
        print(f"\n📊 Session Data Summary:")
        print(f"   Total sessions with data: {len(session_results)}")
        for session_name, data in session_results.items():
            print(f"   - {session_name}: {len(data)} entries")
        
        print()
        
    except Exception as e:
        print(f"❌ Session data loader test failed: {e}")
        import traceback
        traceback.print_exc()

def generate_test_report():
    """Generate a comprehensive test report"""
    print("📋 GENERATING TEST REPORT")
    print("=" * 60)
    
    report = {
        "test_timestamp": "2025-01-XX XX:XX:XX",
        "endpoints_tested": [],
        "working_endpoints": [],
        "failed_endpoints": [],
        "career_stats_working": False,
        "session_data_available": {},
        "recommendations": []
    }
    
    # This would be populated during the actual tests
    print("Test report would be generated here with:")
    print("✅ Working endpoints")
    print("❌ Failed endpoints") 
    print("📊 Available data types")
    print("🔧 Configuration recommendations")
    print("🚀 Next steps for implementation")
    
    print("\nTest complete! Check the logs for detailed results.")

def main():
    """Run all tests in sequence"""
    print("🏁 F1 COMPLETE SYSTEM TEST")
    print("=" * 60)
    print("Testing all F1 API endpoints, career statistics, and session data...")
    print("This will help identify what data is available and working correctly.")
    print()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Run all tests
    test_basic_api_connectivity()
    test_all_2025_endpoints()
    test_specific_race_sessions()
    test_career_statistics()
    test_enhanced_data_service()
    test_session_data_loader()
    generate_test_report()
    
    print("🏁 COMPLETE SYSTEM TEST FINISHED")
    print("=" * 60)
    print("Results:")
    print("✅ Check the console output above for detailed results")
    print("📋 Check logs/f1_system_test.log for complete log")
    print("🔧 Use this information to understand what data is available")
    print()
    print("Next steps:")
    print("1. Review which endpoints are working")
    print("2. Update the UI to handle available data types")
    print("3. Implement error handling for unavailable data")
    print("4. Test the complete application: python main.py")

if __name__ == "__main__":
    main()