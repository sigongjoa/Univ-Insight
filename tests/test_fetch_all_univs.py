import sys
import os
import logging
from src.services.careernet_client import CareerNetClient

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print(">>> [Phase 2] Fetching ALL Universities via CareerNet API")
    
    client = CareerNetClient() # API Key needed for real data
    
    # Mock Mode Check
    if not client.api_key:
        print("⚠️  No API Key found. Running in MOCK mode.")
        print("   (To fetch real data, set CAREERNET_API_KEY env var)")
    
    universities = client.get_all_universities()
    
    print(f"\n✅ Fetched {len(universities)} universities.")
    
    print("\n>>> Sample List:")
    for i, univ in enumerate(universities[:10]):
        print(f"{i+1}. {univ.name} ({univ.region}) - {univ.url}")

if __name__ == "__main__":
    main()
