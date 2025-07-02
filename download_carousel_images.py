"""
Download carousel images for offline use.
This script downloads the carousel images and saves them locally.
"""

import os
import requests
from pathlib import Path


def download_image(url, filename):
    """Download an image from URL and save it locally."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Create the static images directory if it doesn't exist
        images_dir = Path('core/static/core/images')
        images_dir.mkdir(parents=True, exist_ok=True)

        # Save the image
        filepath = images_dir / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"✓ Downloaded: {filename}")
        return True

    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False


def main():
    """Download all carousel images."""
    print("Downloading carousel images...")

    images = [
        {
            'url': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
            'filename': 'school-building.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1577896851231-70ef18881754?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
            'filename': 'students-classroom.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80',
            'filename': 'school-sports.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1562774053-701939374585?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
            'filename': 'school-campus.jpg'
        }
    ]

    success_count = 0
    for image in images:
        if download_image(image['url'], image['filename']):
            success_count += 1

    print(f"\nDownload complete: {success_count}/{len(images)} images downloaded successfully.")

    if success_count > 0:
        print("\nTo use local images, update the template to use:")
        print("{% load static %}")
        print("src=\"{% static 'core/images/school-building.jpg' %}\"")
        print("\nMake sure to run 'python manage.py collectstatic' after downloading images.")


if __name__ == '__main__':
    main()
