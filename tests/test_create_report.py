import time
import unittest

from fastapi.testclient import TestClient

from app.main import app


class CreateReportFeatureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        unique = int(time.time() * 1000)
        cls.email = f"report.tester.{unique}@apps.ipb.ac.id"
        cls.password = "password123"
        register_response = cls.client.post(
            "/auth/register",
            json={
                "email": cls.email,
                "password": cls.password,
                "full_name": "Report Tester",
                "faculty": "FMIPA",
                "nim": f"G64{unique}",
            },
        )
        if register_response.status_code not in (201, 409):
            raise AssertionError(register_response.text)

        login_response = cls.client.post(
            "/auth/login",
            data={"username": cls.email, "password": cls.password},
        )
        if login_response.status_code != 200:
            raise AssertionError(login_response.text)

        cls.headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    def test_create_lost_report_with_frontend_payload_success(self) -> None:
        response = self.client.post(
            "/items",
            headers=self.headers,
            json={
                "name": "AirPods Pro",
                "type": "LOST",
                "category": "Elektronik",
                "location": "Perpustakaan IPB",
                "date": "2026-05-14",
                "time": "10:30",
                "description": "Hilang di meja baca lantai dua.",
                "traits": "Case putih dengan stiker kecil.",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["name"], "AirPods Pro")
        self.assertEqual(body["title"], "AirPods Pro")
        self.assertEqual(body["type"], "LOST")
        self.assertEqual(body["category"], "Elektronik")
        self.assertIsNotNone(body["user_id"])

    def test_create_found_report_with_image_success(self) -> None:
        response = self.client.post(
            "/items",
            headers=self.headers,
            json={
                "name": "Dompet Hitam",
                "type": "FOUND",
                "category": "Dompet / Tas",
                "location": "Kantin Sapta",
                "description": "Ditemukan dekat kasir.",
                "image": "https://example.com/dompet.jpg",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["type"], "FOUND")
        self.assertEqual(body["image"], "https://example.com/dompet.jpg")

    def test_create_report_without_auth_fails(self) -> None:
        response = self.client.post(
            "/items",
            json={
                "name": "Payung Biru",
                "type": "LOST",
                "category": "Lainnya",
                "location": "CCR",
                "description": "Tertinggal setelah kelas.",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_create_report_without_name_fails(self) -> None:
        response = self.client.post(
            "/items",
            headers=self.headers,
            json={
                "type": "LOST",
                "category": "Buku",
                "location": "Perpustakaan IPB",
                "description": "Buku catatan warna cokelat.",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_create_report_with_invalid_type_fails(self) -> None:
        response = self.client.post(
            "/items",
            headers=self.headers,
            json={
                "name": "Kartu KTM",
                "type": "MISSING",
                "category": "Kartu",
                "location": "FEM",
                "description": "Kartu mahasiswa tertinggal.",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_create_report_without_location_fails(self) -> None:
        response = self.client.post(
            "/items",
            headers=self.headers,
            json={
                "name": "Kunci Motor",
                "type": "FOUND",
                "category": "Kunci",
                "description": "Ditemukan di area parkir.",
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
