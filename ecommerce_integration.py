#!/usr/bin/env python3
"""
E-commerce Data Integration Module
Solves the critical pain point of multi-platform data synchronization
"""

import sys
import os
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass
from enum import Enum

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import config

class PlatformType(Enum):
    SHOPIFY = "shopify"
    AMAZON = "amazon"
    EBAY = "ebay"
    WOOCOMMERCE = "woocommerce"
    MAGENTO = "magento"

@dataclass
class ProductData:
    """Standardized product data structure"""
    platform_id: str
    platform_type: PlatformType
    sku: str
    title: str
    price: float
    inventory_quantity: int
    status: str
    last_updated: datetime
    metadata: Dict[str, Any]

class EcommerceDataIntegrator:
    """Specialized E-commerce data integration and synchronization"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        self.logger = logging.getLogger(__name__)
        
    def sync_inventory_across_platforms(self, platforms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sync inventory across multiple e-commerce platforms
        Returns reconciliation report with discrepancies
        """
        self.logger.info(f"Starting inventory sync across {len(platforms)} platforms")
        
        all_products = {}
        sync_issues = []
        
        # Collect data from all platforms
        for platform in platforms:
            try:
                products = self._fetch_platform_data(platform)
                all_products[platform['name']] = products
            except Exception as e:
                sync_issues.append({
                    'platform': platform['name'],
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        # Identify discrepancies
        discrepancies = self._find_inventory_discrepancies(all_products)
        
        # Generate reconciliation report
        report = {
            'total_products': sum(len(products) for products in all_products.values()),
            'discrepancies_found': len(discrepancies),
            'sync_issues': sync_issues,
            'discrepancies': discrepancies,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store sync results
        self._store_sync_results(report)
        
        return report
    
    def _fetch_platform_data(self, platform: Dict[str, Any]) -> List[ProductData]:
        """Fetch product data from specific platform"""
        platform_type = PlatformType(platform['type'])
        
        if platform_type == PlatformType.SHOPIFY:
            return self._fetch_shopify_data(platform)
        elif platform_type == PlatformType.AMAZON:
            return self._fetch_amazon_data(platform)
        elif platform_type == PlatformType.EBAY:
            return self._fetch_ebay_data(platform)
        else:
            raise ValueError(f"Unsupported platform type: {platform_type}")
    
    def _fetch_shopify_data(self, platform: Dict[str, Any]) -> List[ProductData]:
        """Fetch data from Shopify API"""
        headers = {
            'X-Shopify-Access-Token': platform['api_key'],
            'Content-Type': 'application/json'
        }
        
        url = f"https://{platform['shop_domain']}.myshopify.com/admin/api/2023-10/products.json"
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        products = []
        for product in response.json()['products']:
            for variant in product['variants']:
                products.append(ProductData(
                    platform_id=variant['id'],
                    platform_type=PlatformType.SHOPIFY,
                    sku=variant.get('sku', ''),
                    title=product['title'],
                    price=float(variant['price']),
                    inventory_quantity=int(variant['inventory_quantity']),
                    status='active' if product['status'] == 'active' else 'inactive',
                    last_updated=datetime.fromisoformat(variant['updated_at'].replace('Z', '+00:00')),
                    metadata={
                        'product_id': product['id'],
                        'variant_id': variant['id'],
                        'handle': product['handle']
                    }
                ))
        
        return products
    
    def _fetch_amazon_data(self, platform: Dict[str, Any]) -> List[ProductData]:
        """Fetch data from Amazon API (simulated for demo)"""
        # In production, this would use Amazon's SP-API
        products = []
        
        # Simulate Amazon data
        for i in range(10):
            products.append(ProductData(
                platform_id=f"amz_{i}",
                platform_type=PlatformType.AMAZON,
                sku=f"AMZ-SKU-{i}",
                title=f"Amazon Product {i}",
                price=round(19.99 + (i * 2.50), 2),
                inventory_quantity=max(0, 50 - (i * 5)),
                status='active',
                last_updated=datetime.now() - timedelta(hours=i),
                metadata={
                    'asin': f"B0{i:08d}",
                    'category': 'Electronics'
                }
            ))
        
        return products
    
    def _fetch_ebay_data(self, platform: Dict[str, Any]) -> List[ProductData]:
        """Fetch data from eBay API (simulated for demo)"""
        products = []
        
        # Simulate eBay data
        for i in range(8):
            products.append(ProductData(
                platform_id=f"ebay_{i}",
                platform_type=PlatformType.EBAY,
                sku=f"EBAY-SKU-{i}",
                title=f"eBay Product {i}",
                price=round(15.99 + (i * 1.75), 2),
                inventory_quantity=max(0, 30 - (i * 3)),
                status='active',
                last_updated=datetime.now() - timedelta(hours=i*2),
                metadata={
                    'item_id': f"12345678{i}",
                    'category_id': '11450'
                }
            ))
        
        return products
    
    def _find_inventory_discrepancies(self, all_products: Dict[str, List[ProductData]]) -> List[Dict[str, Any]]:
        """Find inventory discrepancies across platforms"""
        discrepancies = []
        
        # Group products by SKU across platforms
        sku_groups = {}
        for platform_name, products in all_products.items():
            for product in products:
                if product.sku:
                    if product.sku not in sku_groups:
                        sku_groups[product.sku] = {}
                    sku_groups[product.sku][platform_name] = product
        
        # Check for discrepancies
        for sku, platform_products in sku_groups.items():
            if len(platform_products) > 1:
                # Check for price discrepancies
                prices = [p.price for p in platform_products.values()]
                if max(prices) - min(prices) > 0.01:  # More than 1 cent difference
                    discrepancies.append({
                        'sku': sku,
                        'type': 'price_discrepancy',
                        'platforms': list(platform_products.keys()),
                        'prices': {p: platform_products[p].price for p in platform_products},
                        'severity': 'high' if max(prices) - min(prices) > 5.0 else 'medium'
                    })
                
                # Check for inventory discrepancies
                quantities = [p.inventory_quantity for p in platform_products.values()]
                if max(quantities) - min(quantities) > 0:
                    discrepancies.append({
                        'sku': sku,
                        'type': 'inventory_discrepancy',
                        'platforms': list(platform_products.keys()),
                        'quantities': {p: platform_products[p].inventory_quantity for p in platform_products},
                        'severity': 'high' if max(quantities) - min(quantities) > 10 else 'medium'
                    })
        
        return discrepancies
    
    def _store_sync_results(self, report: Dict[str, Any]):
        """Store sync results in database"""
        # Convert datetime objects to ISO strings for JSON serialization
        serializable_report = {}
        for key, value in report.items():
            if isinstance(value, datetime):
                serializable_report[key] = value.isoformat()
            elif isinstance(value, list):
                serializable_report[key] = []
                for item in value:
                    if isinstance(item, dict):
                        serializable_item = {}
                        for item_key, item_value in item.items():
                            if isinstance(item_value, datetime):
                                serializable_item[item_key] = item_value.isoformat()
                            else:
                                serializable_item[item_key] = item_value
                        serializable_report[key].append(serializable_item)
                    else:
                        serializable_report[key].append(item)
            else:
                serializable_report[key] = value
        
        sync_record = {
            'source_id': 'ecommerce_sync',
            'data_type': 'sync_report',
            'value': len(report['discrepancies']),
            'timestamp': datetime.now(),
            'metadata': serializable_report
        }
        
        self.db_manager.store_data([sync_record])
    
    def generate_revenue_impact_report(self) -> Dict[str, Any]:
        """Generate report showing potential revenue impact of sync issues"""
        # Fetch recent sync data
        recent_data = self.db_manager.get_data(
            data_type='sync_report',
            start_date=datetime.now() - timedelta(days=7),
            limit=100
        )
        
        total_discrepancies = sum(record['value'] for record in recent_data)
        estimated_revenue_loss = total_discrepancies * 25.0  # Average $25 per discrepancy
        
        return {
            'total_discrepancies': total_discrepancies,
            'estimated_revenue_loss': estimated_revenue_loss,
            'sync_frequency': 'daily',
            'last_sync': datetime.now().isoformat(),
            'recommendations': [
                'Implement automated inventory sync',
                'Set up price monitoring alerts',
                'Establish real-time data validation'
            ]
        }

def main():
    """Demo the E-commerce integration capabilities"""
    integrator = EcommerceDataIntegrator()
    
    # Sample platform configurations
    platforms = [
        {
            'name': 'My Shopify Store',
            'type': 'shopify',
            'shop_domain': 'my-store',
            'api_key': 'demo_key'
        },
        {
            'name': 'Amazon Seller Account',
            'type': 'amazon',
            'api_key': 'demo_key'
        },
        {
            'name': 'eBay Store',
            'type': 'ebay',
            'api_key': 'demo_key'
        }
    ]
    
    # Run inventory sync
    print("🔄 Running E-commerce Inventory Sync...")
    sync_report = integrator.sync_inventory_across_platforms(platforms)
    
    print(f"✅ Sync completed!")
    print(f"📊 Total products processed: {sync_report['total_products']}")
    print(f"⚠️  Discrepancies found: {sync_report['discrepancies_found']}")
    
    # Generate revenue impact report
    revenue_report = integrator.generate_revenue_impact_report()
    print(f"💰 Estimated revenue impact: ${revenue_report['estimated_revenue_loss']:.2f}")
    
    return sync_report

if __name__ == "__main__":
    main() 