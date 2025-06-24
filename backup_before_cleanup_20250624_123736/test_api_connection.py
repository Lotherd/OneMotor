# test_api_connection.py
"""
Script para probar la conectividad con la nueva API de Jolpica
Ejecutar este script independientemente antes de actualizar la aplicación
"""

import sys
import json
import requests
from datetime import datetime

def test_jolpica_api():
    """Probar conectividad con Jolpica API"""
    
    print("=" * 60)
    print("🏎️  PRUEBA DE CONECTIVIDAD - JOLPICA F1 API")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs a probar
    test_urls = [
        "http://api.jolpi.ca/ergast/f1/current/driverStandings.json",
        "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
    ]
    
    headers = {
        'User-Agent': 'F1Dashboard/1.1 (Test Script)',
        'Accept': 'application/json'
    }
    
    for i, url in enumerate(test_urls, 1):
        print(f"🔍 Prueba {i}: {url}")
        print("-" * 50)
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # Imprimir status
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verificar estructura de datos
                    if 'MRData' in data:
                        mr_data = data['MRData']
                        print(f"✅ API Response OK")
                        print(f"   Series: {mr_data.get('series', 'N/A')}")
                        print(f"   Total: {mr_data.get('total', 'N/A')}")
                        
                        # Verificar standings
                        if 'StandingsTable' in mr_data:
                            standings_table = mr_data['StandingsTable']
                            if 'StandingsLists' in standings_table:
                                standings_lists = standings_table['StandingsLists']
                                if standings_lists and len(standings_lists) > 0:
                                    driver_standings = standings_lists[0].get('DriverStandings', [])
                                    print(f"   Drivers Found: {len(driver_standings)}")
                                    
                                    # Mostrar top 3
                                    if driver_standings:
                                        print("   Top 3 Drivers:")
                                        for j, driver in enumerate(driver_standings[:3], 1):
                                            driver_info = driver.get('Driver', {})
                                            name = f"{driver_info.get('givenName', '')} {driver_info.get('familyName', '')}"
                                            points = driver.get('points', 0)
                                            print(f"      {j}. {name} - {points} pts")
                                    
                                    print(f"🎉 SUCCESS: API está funcionando correctamente!")
                                    return True
                        
                        print(f"⚠️  WARNING: Estructura de datos incompleta")
                    else:
                        print(f"❌ ERROR: Estructura de respuesta inesperada")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ ERROR: Respuesta no es JSON válido - {e}")
                    
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"   Reason: {response.reason}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"❌ ERROR: Timeout de conexión")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ ERROR: Error de conexión - {e}")
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__} - {e}")
        
        print()
    
    print("❌ RESULTADO: Ninguna URL funcionó correctamente")
    return False

def test_old_ergast():
    """Probar si la API antigua de Ergast sigue funcionando"""
    print("🔍 Probando API antigua de Ergast...")
    print("-" * 50)
    
    try:
        url = "http://ergast.com/api/f1/current/driverStandings.json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Ergast antigua sigue funcionando")
            return True
        else:
            print(f"❌ Ergast antigua: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Ergast antigua: {type(e).__name__} - {e}")
    
    return False

def show_recommendations():
    """Mostrar recomendaciones basadas en los resultados"""
    print("\n" + "=" * 60)
    print("📋 RECOMENDACIONES")
    print("=" * 60)
    print("""
1. ✅ Actualiza tu archivo config/settings.py con:
   ERGAST_BASE_URL = "http://api.jolpi.ca/ergast/f1"

2. ✅ Reemplaza el archivo services/api_client.py con la versión actualizada

3. ✅ La aplicación debería funcionar normalmente después de estos cambios

4. ℹ️  Jolpica tiene un límite de 200 requests/hora sin autenticación

5. ℹ️  En caso de problemas, puedes intentar con HTTPS:
   ERGAST_BASE_URL = "https://api.jolpi.ca/ergast/f1"

6. 🔄 Si necesitas más requests, contacta al equipo de Jolpica en:
   https://github.com/jolpica/jolpica-f1
""")

if __name__ == "__main__":
    print("Iniciando prueba de conectividad...\n")
    
    # Probar nueva API
    jolpica_works = test_jolpica_api()
    
    # Probar API antigua
    ergast_works = test_old_ergast()
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Jolpica API (nueva): {'✅ Funciona' if jolpica_works else '❌ No funciona'}")
    print(f"Ergast API (antigua): {'✅ Funciona' if ergast_works else '❌ No funciona'}")
    
    if jolpica_works:
        print("\n🎉 ¡Excelente! Jolpica API está funcionando.")
        show_recommendations()
    elif ergast_works:
        print("\n⚠️  Ergast antigua funciona, pero será descontinuada.")
        print("   Recomendamos cambiar a Jolpica pronto.")
    else:
        print("\n❌ Ninguna API funciona. Verifica tu conexión a internet.")
    
    print("\n" + "=" * 60)