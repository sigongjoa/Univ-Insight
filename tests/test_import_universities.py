
import pytest
import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models import Base, University
from src.scripts.import_universities import import_universities

# Setup in-memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_csv(tmp_path):
    file_path = tmp_path / "test_universities.csv"
    headers = [
        "학교명", "학교 영문명", "본분교구분명", "대학구분명", "학교구분명", "설립형태구분명", 
        "시도코드", "시도명", "소재지도로명주소", "소재지지번주소", "도로명우편번호", 
        "소재지우편번호", "홈페이지주소", "대표전화번호", "대표팩스번호", "설립일자", 
        "기준연도", "데이터기준일자", "제공기관코드", "제공기관명"
    ]
    data = [
        {
            "학교명": "테스트대학교",
            "학교 영문명": "Test University",
            "소재지도로명주소": "Seoul, Korea",
            "홈페이지주소": "http://test.ac.kr",
            "설립일자": "2023-01-01"
        },
        {
            "학교명": "샘플대학교",
            "학교 영문명": "Sample College",
            "소재지도로명주소": "Busan, Korea",
            "홈페이지주소": "http://sample.ac.kr",
            "설립일자": "1990-05-05"
        }
    ]
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            # Fill missing keys with empty strings
            full_row = {k: row.get(k, "") for k in headers}
            writer.writerow(full_row)
            
    return str(file_path)

def test_import_universities(db, mock_csv):
    """
    UC-001 Backend Test: Verify that universities are correctly imported from CSV.
    """
    # Run import
    import_universities(mock_csv, db)
    
    # Verify
    universities = db.query(University).all()
    assert len(universities) == 2
    
    u1 = db.query(University).filter(University.name == "Test University").first()
    assert u1 is not None
    assert u1.id == "test-university"
    assert u1.name_ko == "테스트대학교"
    assert u1.established_year == 2023
    
    u2 = db.query(University).filter(University.name == "Sample College").first()
    assert u2 is not None
    assert u2.id == "sample-college"
