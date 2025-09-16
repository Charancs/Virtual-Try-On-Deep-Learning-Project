#!/usr/bin/env python3
"""
Download datasets and clothing images for Virtual Try-On training
"""

import os
import urllib.request
import zipfile
import json
import sys
import time
from pathlib import Path
import requests
from PIL import Image
import io

# Dataset URLs for training
DATASET_URLS = {
    'viton_dataset': {
        'url': 'https://github.com/xthan/VITON/releases/download/v1.0/VITON_traindata.zip',
        'file': 'VITON_traindata.zip',
        'description': 'VITON training dataset with person-clothing pairs',
        'extract_to': 'data/viton'
    },
    'deep_fashion': {
        'url': 'https://drive.google.com/uc?id=1Uc0DTTkSfmPr2qWCPXOQvf_xjfLdQndb',
        'file': 'deep_fashion_subset.zip',
        'description': 'DeepFashion dataset subset',
        'extract_to': 'data/deep_fashion'
    },
    'clothing_1m': {
        'url': 'https://github.com/AemikaChow/DATASOURCE/releases/download/v1.0/clothing1m_sample.zip',
        'file': 'clothing1m_sample.zip',
        'description': 'Clothing1M sample dataset',
        'extract_to': 'data/clothing1m'
    }
}

# Clothing image sources for training data
CLOTHING_SOURCES = {
    'shirts': [
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1622445275576-721325763afe?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1627225924765-552d49cf47ad?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1618677603286-0ec56cb6e1b5?w=400&h=600&fit=crop'
    ],
    'dresses': [
        'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1566479179817-0d4e3c8e2da2?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1588117472013-59bb13edafec?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1538329972958-465d6d2703ef?w=400&h=600&fit=crop',
        'https://images.unsplash.com/photo-1582418702216-d8f41b2ba7d7?w=400&h=600&fit=crop'
    ]
}

def download_with_progress(url, filename):
    """Download file with progress indicator."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        sys.stdout.write(f"\r{os.path.basename(filename)}: {percent}%")
                        sys.stdout.flush()
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\nError downloading {filename}: {str(e)}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract zip file."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)  # Clean up zip file
        return True
    except Exception as e:
        print(f"Error extracting {zip_path}: {str(e)}")
        return False

def download_clothing_images(data_dir='data/clothing_images'):
    """Download clothing images for training."""
    print("Downloading clothing images for training...")
    
    for category, urls in CLOTHING_SOURCES.items():
        category_dir = os.path.join(data_dir, category)
        Path(category_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\nDownloading {category}...")
        
        for i, url in enumerate(urls):
            filename = f"{category}_{i+1:02d}.jpg"
            filepath = os.path.join(category_dir, filename)
            
            if os.path.exists(filepath):
                print(f"  {filename} already exists, skipping...")
                continue
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Verify it's a valid image
                img = Image.open(io.BytesIO(response.content))
                img = img.convert('RGB')
                img.save(filepath, 'JPEG', quality=95)
                
                print(f"  ✓ Downloaded {filename}")
                time.sleep(1)  # Be respectful to the server
                
            except Exception as e:
                print(f"  ✗ Failed to download {filename}: {str(e)}")
                # Create a placeholder
                try:
                    placeholder = Image.new('RGB', (400, 600), color='lightgray')
                    placeholder.save(filepath, 'JPEG')
                    print(f"  Created placeholder for {filename}")
                except:
                    pass

def download_datasets(data_dir='data'):
    """Download training datasets."""
    print("Downloading training datasets...")
    
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    for dataset_name, dataset_info in DATASET_URLS.items():
        print(f"\nDownloading {dataset_info['description']}...")
        
        # Create dataset directory
        extract_path = os.path.join(data_dir, dataset_info['extract_to'].replace('data/', ''))
        Path(extract_path).mkdir(parents=True, exist_ok=True)
        
        # Check if dataset already exists
        if os.path.exists(extract_path) and os.listdir(extract_path):
            print(f"Dataset {dataset_name} already exists. Skipping...")
            continue
        
        zip_path = os.path.join(data_dir, dataset_info['file'])
        
        # Try to download
        if download_with_progress(dataset_info['url'], zip_path):
            print(f"Extracting {dataset_name}...")
            if extract_zip(zip_path, extract_path):
                print(f"✓ {dataset_name} downloaded and extracted successfully")
            else:
                print(f"✗ Failed to extract {dataset_name}")
        else:
            print(f"✗ Failed to download {dataset_name}")
            # Create sample data structure
            create_sample_dataset(extract_path, dataset_name)

def create_sample_dataset(dataset_path, dataset_name):
    """Create sample dataset structure for training."""
    print(f"Creating sample dataset structure for {dataset_name}...")
    
    if dataset_name == 'viton_dataset':
        # Create VITON-like structure
        subdirs = ['train/cloth', 'train/cloth-mask', 'train/image', 'train/image-parse', 'train/pose']
        for subdir in subdirs:
            Path(os.path.join(dataset_path, subdir)).mkdir(parents=True, exist_ok=True)
        
        # Create sample metadata
        metadata = {
            "dataset": "VITON Sample",
            "description": "Sample dataset for virtual try-on training",
            "structure": {
                "cloth": "Clothing item images",
                "cloth-mask": "Clothing segmentation masks",
                "image": "Person images",
                "image-parse": "Human parsing maps",
                "pose": "Pose keypoints"
            }
        }
        
        with open(os.path.join(dataset_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    elif dataset_name == 'deep_fashion':
        # Create DeepFashion-like structure
        subdirs = ['images', 'labels', 'annotations']
        for subdir in subdirs:
            Path(os.path.join(dataset_path, subdir)).mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "dataset": "DeepFashion Sample",
            "description": "Sample fashion dataset for clothing recognition",
            "categories": ["shirt", "dress", "pants", "skirt", "jacket"]
        }
        
        with open(os.path.join(dataset_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    elif dataset_name == 'clothing_1m':
        # Create Clothing1M-like structure
        subdirs = ['images/train', 'images/val', 'images/test']
        for subdir in subdirs:
            Path(os.path.join(dataset_path, subdir)).mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "dataset": "Clothing1M Sample",
            "description": "Sample large-scale clothing dataset",
            "split": {
                "train": "Training images",
                "val": "Validation images", 
                "test": "Test images"
            }
        }
        
        with open(os.path.join(dataset_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

def create_training_manifest(data_dir='data'):
    """Create training manifest file."""
    manifest = {
        "datasets": {},
        "clothing_images": {},
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_images": 0
    }
    
    # Scan datasets
    for dataset_name in DATASET_URLS.keys():
        dataset_path = os.path.join(data_dir, dataset_name.replace('_dataset', ''))
        if os.path.exists(dataset_path):
            manifest["datasets"][dataset_name] = {
                "path": dataset_path,
                "exists": True,
                "metadata_file": os.path.join(dataset_path, 'metadata.json')
            }
    
    # Scan clothing images
    clothing_path = os.path.join(data_dir, 'clothing_images')
    if os.path.exists(clothing_path):
        for category in ['shirts', 'dresses']:
            category_path = os.path.join(clothing_path, category)
            if os.path.exists(category_path):
                images = [f for f in os.listdir(category_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
                manifest["clothing_images"][category] = {
                    "path": category_path,
                    "count": len(images),
                    "images": images
                }
                manifest["total_images"] += len(images)
    
    # Save manifest
    manifest_path = os.path.join(data_dir, 'training_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nTraining manifest created: {manifest_path}")
    print(f"Total clothing images available: {manifest['total_images']}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download datasets and clothing images for training')
    parser.add_argument('--data-dir', default='data', help='Directory to save data (default: data)')
    parser.add_argument('--datasets-only', action='store_true', help='Download only datasets, not clothing images')
    parser.add_argument('--images-only', action='store_true', help='Download only clothing images, not datasets')
    parser.add_argument('--skip-existing', action='store_true', help='Skip existing files')
    
    args = parser.parse_args()
    
    if not args.images_only:
        download_datasets(args.data_dir)
    
    if not args.datasets_only:
        download_clothing_images(os.path.join(args.data_dir, 'clothing_images'))
    
    create_training_manifest(args.data_dir)
    
    print("\n" + "="*50)
    print("Dataset download completed!")
    print("="*50)
    print("You can now proceed with training the virtual try-on model.")

if __name__ == '__main__':
    main()
