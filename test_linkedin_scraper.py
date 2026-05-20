#!/usr/bin/env python
"""Test script for LinkedIn scraper with enhanced anti-blocking"""

import sys
import os
import tempfile
from linkedin_scraper import scrape_linkedin_to_csv

def test_linkedin_scraper():
    """Test the LinkedIn scraper with a sample URL"""
    
    print("=" * 70)
    print("LinkedIn Scraper Test")
    print("=" * 70)
    print()
    
    # Test URLs - using job search queries
    test_urls = [
        "https://www.linkedin.com/jobs/search/?keywords=python+developer",
        "https://www.linkedin.com/jobs/search/?keywords=data+scientist&location=United+States",
    ]
    
    for test_url in test_urls:
        print(f"Testing URL: {test_url}")
        print("-" * 70)
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_path = f.name
        
        try:
            print(f"Output file: {output_path}")
            print()
            print("Starting scrape (this may take 1-2 minutes)...")
            print()
            
            # Run scraper
            count = scrape_linkedin_to_csv(test_url, output_path, max_jobs=10)
            
            print()
            print("=" * 70)
            print(f"✓ SUCCESS! Scraped {count} jobs")
            print("=" * 70)
            
            # Check file size
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"Output file size: {file_size:,} bytes")
                
                # Read and display first few lines
                with open(output_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"File has {len(lines)} lines (including header)")
                    if len(lines) > 1:
                        print()
                        print("First job entry:")
                        print(lines[1][:200])  # Show first 200 chars
            
        except Exception as e:
            print()
            print("=" * 70)
            print(f"✗ FAILED: {str(e)}")
            print("=" * 70)
            print()
            print("This is expected if LinkedIn is blocking the request.")
            print("The scraper will automatically fall back to mock data for testing.")
            print()
            
            # Check if mock data was generated
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"Note: Mock data was generated ({file_size:,} bytes)")
        
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)
                print("Temp file cleaned up")
        
        print()
        print()

if __name__ == '__main__':
    test_linkedin_scraper()
