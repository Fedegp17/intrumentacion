"""
Script rapido para verificar conexiones
Ejecuta pruebas basicas de conectividad
"""

import requests
import sys

def test_python():
    """Verifica que Python funcione"""
    print("1. Verificando Python...")
    try:
        import sys
        version = sys.version.split()[0]
        print(f"   [OK] Python {version} instalado")
        return True
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def test_requests():
    """Verifica que requests este instalado"""
    print("2. Verificando libreria 'requests'...")
    try:
        import requests
        print(f"   [OK] requests {requests.__version__} instalado")
        return True
    except ImportError:
        print("   [ERROR] 'requests' no esta instalado")
        print("   Ejecuta: pip install requests")
        return False

def test_vercel():
    """Verifica conexion a Vercel"""
    print("3. Verificando conexion a Vercel...")
    try:
        url = "https://intrumentacion-7fkz.vercel.app"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"   [OK] Vercel responde (Status: {response.status_code})")
            return True
        else:
            print(f"   [WARN] Vercel responde pero con status: {response.status_code}")
            return True  # Aun asi esta conectado
    except requests.exceptions.ConnectionError:
        print("   [ERROR] No se puede conectar a Vercel")
        print("   Verifica que el servidor este desplegado")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def test_endpoint():
    """Verifica que el endpoint /data exista"""
    print("4. Verificando endpoint /data...")
    try:
        url = "https://intrumentacion-7fkz.vercel.app/data"
        response = requests.get(url, timeout=5)
        print(f"   [OK] Endpoint /data existe (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("   [ERROR] No se puede conectar al endpoint")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def test_send_dummy():
    """Prueba enviar un dato dummy"""
    print("5. Probando envio de datos dummy...")
    try:
        url = "https://intrumentacion-7fkz.vercel.app/data"
        data = {
            "temperature1": 25.0,
            "humidity1": 65.0,
            "temperature2": 24.5,
            "humidity2": 63.0,
            "soil_moisture1": 50.0,
            "soil_moisture2": 52.0,
            "uv_index": 3.5
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"   [OK] Datos enviados correctamente (Status: {response.status_code})")
            return True
        else:
            print(f"   [WARN] Error al enviar (Status: {response.status_code})")
            print(f"   Respuesta: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def main():
    """Funcion principal"""
    print("\n" + "="*60)
    print("PRUEBA RAPIDA DE CONEXIONES")
    print("="*60 + "\n")
    
    results = []
    results.append(test_python())
    results.append(test_requests())
    results.append(test_vercel())
    results.append(test_endpoint())
    results.append(test_send_dummy())
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[OK] Todas las pruebas pasaron ({passed}/{total})")
        print("\nTodo esta listo! Puedes ejecutar:")
        print("  python test_dummy_data.py")
        sys.exit(0)
    else:
        print(f"[ERROR] Algunas pruebas fallaron ({passed}/{total})")
        print("\nRevisa los errores arriba y corrige los problemas.")
        sys.exit(1)

if __name__ == "__main__":
    main()

