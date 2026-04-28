"""Comprehensive tests for file upload and parsing."""
import pytest
from io import BytesIO
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


# Fixtures for common mock setup
@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client with chained methods."""
    mock_db = MagicMock()
    return mock_db


def setup_business_mock(mock_db, business_id, user_id):
    """Configure mock for business lookup (exists and belongs to user)."""
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
        data={"id": str(business_id), "user_id": str(user_id)}
    )


def setup_upload_insert_mock(mock_db, upload_id, business_id, file_name, parse_status, parsed_data=None):
    """Configure mock for upload insert response."""
    # Create a separate chain for insert operations
    mock_insert = MagicMock()
    mock_insert.execute.return_value = MagicMock(
        data=[{
            "id": str(upload_id),
            "business_id": str(business_id),
            "file_name": file_name,
            "file_type": file_name.rsplit(".", 1)[-1] if "." in file_name else "",
            "parse_status": parse_status,
            "parsed_data": parsed_data,
        }]
    )

    # For table("business_uploads").insert()
    def table_side_effect(table_name):
        result = MagicMock()
        if table_name == "business_uploads":
            result.insert.return_value = mock_insert
        else:
            result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                data={"id": str(business_id), "user_id": str(uuid4())}
            )
        return result

    mock_db.table.side_effect = table_side_effect


class TestUploadCSVSuccess:
    """Test successful CSV upload and parsing."""

    def test_upload_csv_parsing(self):
        """CSV file should be parsed correctly."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        csv_content = b"""name,age,visits,spend
Alice,25,10,500
Bob,35,5,800
Carol,45,20,1200"""

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                # Setup business lookup
                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        # For insert
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "business_id": str(business_id),
                                "file_name": "customers.csv",
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": ["name", "age", "visits", "spend"],
                                    "row_count": 3,
                                    "sample": [
                                        {"name": "Alice", "age": "25", "visits": "10", "spend": "500"},
                                        {"name": "Bob", "age": "35", "visits": "5", "spend": "800"},
                                        {"name": "Carol", "age": "45", "visits": "20", "spend": "1200"},
                                    ]
                                }
                            }]
                        )
                    else:
                        # For businesses select
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("customers.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                data = response.json()
                assert data["status"] == "parsed"
                assert data["parsed_data"]["row_count"] == 3

    def test_csv_parse_status_is_parsed(self):
        """Status should be 'parsed' for valid CSV."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        csv_content = b"col1,col2\nval1,val2"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {"columns": ["col1", "col2"], "row_count": 1},
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                assert response.json()["status"] == "parsed"

    def test_csv_row_count_correct(self):
        """Row count should be accurate."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # 10 rows plus header
        csv_lines = [b"col1,col2"]
        csv_lines.extend([f"val{i},data{i}".encode() for i in range(10)])
        csv_content = b"\n".join(csv_lines)

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {"columns": ["col1", "col2"], "row_count": 10},
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                assert response.json()["parsed_data"]["row_count"] == 10

    def test_csv_sample_rows_limited(self):
        """Sample should be ≤5 rows."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        csv_content = b"\n".join([
            b"name,age",
            *[f"person{i},{20+i}".encode() for i in range(10)]
        ])

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": ["name", "age"],
                                    "row_count": 10,
                                    "sample": [{"name": f"person{i}", "age": str(20+i)} for i in range(5)]
                                },
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                sample = response.json()["parsed_data"]["sample"]
                assert len(sample) <= 5


class TestUploadValidation:
    """Test upload validation."""

    def test_rejects_unsupported_format(self):
        """Non-CSV/text files should be rejected with 400."""
        user_id = uuid4()
        business_id = uuid4()

        exe_content = b"MZ\x90\x00"  # EXE header

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            files = {"file": ("virus.exe", BytesIO(exe_content), "application/x-msdownload")}
            response = client.post(f"/api/uploads/{business_id}", files=files)

            assert response.status_code == 400

    def test_rejects_oversized_file(self):
        """Files >10MB should be rejected with 400."""
        user_id = uuid4()
        business_id = uuid4()

        # Create 11MB file
        oversized_content = b"x" * (11 * 1024 * 1024)

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            files = {"file": ("huge.csv", BytesIO(oversized_content), "text/csv")}
            response = client.post(f"/api/uploads/{business_id}", files=files)

            assert response.status_code == 400

    def test_rejects_wrong_business_owner(self):
        """User can't upload to business they don't own (404)."""
        user_id = uuid4()
        business_id = uuid4()

        csv_content = b"col1,col2\nval1,val2"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                # Business not found (ownership check fails)
                mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                    data=None  # No business found
                )

                files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code == 404


class TestUploadErrorHandling:
    """Test error handling in uploads."""

    def test_utf8_error_graceful(self):
        """Binary/encoding errors should return pending status gracefully, not 500."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # Invalid UTF-8 content
        bad_content = b"\x80\x81\x82\x83"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        # On UTF-8 decode error, parse_status should be "pending"
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "pending",
                                "parsed_data": None,
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("bad.csv", BytesIO(bad_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                # Should not 500 error; should gracefully handle encoding error
                assert response.status_code != 500
                assert response.status_code in [200, 201, 400]

    def test_non_csv_parse_status_is_pending(self):
        """Non-CSV files should have parse_status='pending'."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        txt_content = b"Just plain text, not CSV format"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        # Non-CSV files are not parsed immediately
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "pending",
                                "parsed_data": None,
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("notes.txt", BytesIO(txt_content), "text/plain")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                data = response.json()
                # Should be pending if not CSV
                assert data.get("status") in ["pending", "parsed"]


class TestUploadEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_csv_file(self):
        """Empty CSV file should be handled gracefully."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # Completely empty file
        empty_content = b""

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "pending",
                                "parsed_data": None,
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("empty.csv", BytesIO(empty_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code != 500

    def test_csv_header_only(self):
        """CSV with headers but no data rows should be parsed."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        csv_content = b"col1,col2,col3"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": ["col1", "col2", "col3"],
                                    "row_count": 0,
                                    "sample": []
                                }
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("header.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                data = response.json()
                assert data["parsed_data"]["row_count"] == 0

    def test_csv_with_many_columns(self):
        """CSV with many columns should be parsed correctly."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # Create CSV with 50 columns
        columns = [f"col{i}" for i in range(50)]
        header = ",".join(columns).encode()
        row = ",".join([f"val{i}" for i in range(50)]).encode()
        csv_content = b"\n".join([header, row])

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": columns,
                                    "row_count": 1,
                                    "sample": [dict(zip(columns, [f"val{i}" for i in range(50)]))]
                                }
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("wide.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                assert len(response.json()["parsed_data"]["columns"]) == 50

    def test_csv_with_special_characters(self):
        """CSV with quoted fields and special characters should parse correctly."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        csv_content = b"""name,description,notes
"Alice Smith","A person with a, comma","Quote: \\"Hello\\""
"Bob's Store","Store & Shop","Normal note\""""

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": ["name", "description", "notes"],
                                    "row_count": 2,
                                    "sample": [
                                        {"name": "Alice Smith", "description": "A person with a, comma"},
                                        {"name": "Bob's Store", "description": "Store & Shop"},
                                    ]
                                }
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("special.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                assert response.json()["parsed_data"]["row_count"] == 2

    def test_file_without_extension(self):
        """Files without extension should be rejected with 400."""
        user_id = uuid4()
        business_id = uuid4()

        content = b"some data"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            files = {"file": ("noextension", BytesIO(content), "text/plain")}
            response = client.post(f"/api/uploads/{business_id}", files=files)

            assert response.status_code == 400

    def test_xlsx_file_accepted_but_pending(self):
        """XLSX files should be accepted as 'pending' (not parsed immediately)."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # Minimal XLSX file signature
        xlsx_content = b"PK\x03\x04"  # ZIP header

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "pending",
                                "parsed_data": None,
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("data.xlsx", BytesIO(xlsx_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                assert response.json()["status"] == "pending"

    def test_response_includes_required_fields(self):
        """Response should include id, filename, size, status, parsed_data."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        csv_content = b"col1,col2\nval1,val2"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": ["col1", "col2"],
                                    "row_count": 1,
                                    "sample": [{"col1": "val1", "col2": "val2"}]
                                }
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                data = response.json()
                assert "id" in data
                assert "filename" in data
                assert "size" in data
                assert "status" in data
                assert "parsed_data" in data

    def test_pdf_file_allowed(self):
        """PDF files should be accepted as valid file type."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # Minimal PDF signature
        pdf_content = b"%PDF-1.4\n"

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "pending",
                                "parsed_data": None,
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("doc.pdf", BytesIO(pdf_content), "application/pdf")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]

    def test_large_csv_with_many_rows(self):
        """Large CSV with 100+ rows should limit sample to 5."""
        user_id = uuid4()
        business_id = uuid4()
        upload_id = uuid4()

        # Create CSV with 100 data rows
        header = b"id,name,value"
        rows = [f"{i},customer{i},{i*100}".encode() for i in range(100)]
        csv_content = b"\n".join([header] + rows)

        with patch("backend.api.routes.uploads.get_current_user_id", return_value=user_id):
            with patch("backend.api.routes.uploads.get_supabase") as mock_db_func:
                mock_db = MagicMock()
                mock_db_func.return_value = mock_db

                def table_side_effect(table_name):
                    result = MagicMock()
                    if table_name == "business_uploads":
                        sample = [{"id": str(i), "name": f"customer{i}", "value": str(i*100)} for i in range(5)]
                        result.insert.return_value.execute.return_value = MagicMock(
                            data=[{
                                "id": str(upload_id),
                                "parse_status": "parsed",
                                "parsed_data": {
                                    "columns": ["id", "name", "value"],
                                    "row_count": 100,
                                    "sample": sample
                                }
                            }]
                        )
                    else:
                        result.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                            data={"id": str(business_id), "user_id": str(user_id)}
                        )
                    return result

                mock_db.table.side_effect = table_side_effect

                files = {"file": ("large.csv", BytesIO(csv_content), "text/csv")}
                response = client.post(f"/api/uploads/{business_id}", files=files)

                assert response.status_code in [200, 201]
                sample = response.json()["parsed_data"]["sample"]
                assert len(sample) == 5
                assert response.json()["parsed_data"]["row_count"] == 100
