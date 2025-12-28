import unittest
import requests
import json

class TestSwaggerDocumentation(unittest.TestCase):
    # Backend uygulamasının çalıştığı adres (Lokalde genelde 8000 veya 5000 portudur)
    # Esra'nın koduna göre burayı güncellemen gerekebilir.
    BASE_URL = "http://localhost:8000" 
    OPENAPI_URL = f"{BASE_URL}/openapi.json"  # FastAPI için standart URL

    def test_swagger_schema_availability(self):
        """
        Swagger/OpenAPI JSON şemasının erişilebilir olduğunu (200 OK) kontrol eder.
        """
        try:
            response = requests.get(self.OPENAPI_URL)
            self.assertEqual(response.status_code, 200, "OpenAPI şemasına erişilemiyor!")
            self.schema = response.json()
        except requests.exceptions.ConnectionError:
            self.fail("Backend sunucusu çalışmıyor olabilir. Testi çalıştırmadan önce sunucuyu başlatın.")

    def test_required_endpoints_exist(self):
        """
        Raporda belirtilen kritik uç noktaların (/register ve /audit) 
        dokümantasyonda tanımlı olup olmadığını kontrol eder.
        """
        response = requests.get(self.OPENAPI_URL)
        schema = response.json()
        paths = schema.get("paths", {})

        # 1. /register endpoint kontrolü
        self.assertIn("/register", paths, "HATA: /register uç noktası dokümantasyonda bulunamadı!")
        
        # 2. /audit endpoint kontrolü
        self.assertIn("/audit", paths, "HATA: /audit uç noktası dokümantasyonda bulunamadı!")

    def test_endpoint_documentation_standards(self):
        """
        Uç noktaların açıklama (description) ve özet (summary) alanlarının
        dolu olduğunu kontrol eder (Kalite Kontrol).
        """
        response = requests.get(self.OPENAPI_URL)
        schema = response.json()
        paths = schema.get("paths", {})

        for endpoint in ["/register", "/audit"]:
            if endpoint in paths:
                methods = paths[endpoint]
                # Genelde POST veya GET metoduna bakılır
                for method in methods:
                    details = methods[method]
                    
                    # Summary kontrolü
                    self.assertTrue(
                        "summary" in details and len(details["summary"]) > 0,
                        f"{endpoint} [{method}] için 'Summary' alanı eksik!"
                    )
                    
                    # Description kontrolü (Detaylı dokümantasyon için)
                    self.assertTrue(
                        "description" in details and len(details["description"]) > 0,
                        f"{endpoint} [{method}] için 'Description' alanı eksik!"
                    )

if __name__ == '__main__':
    unittest.main()