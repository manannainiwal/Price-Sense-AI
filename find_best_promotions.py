"""
Find optimal promotion combinations
Tests various discount % and duration combinations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from modules.data_loader import data_loader
from modules.promotion_analyzer import PromotionAnalyzer
import pandas as pd


def test_all_scenarios(product_id: str):
    """
    Test all discount/duration combinations for a product
    """
    # Load data
    products = data_loader.load_product_catalog()
    business_rules = data_loader.get_business_rules()
    
    product = data_loader.get_product_by_id(product_id)
    if not product:
        print(f"❌ Product {product_id} not found")
        return
    
    print(f"\n🎯 Testing Promotions for: {product['name']}")
    print(f"   Base Price: ${product['base_price']:.2f}")
    print(f"   Current Margin: {product['margin']*100:.0f}%")
    print("=" * 80)
    
    # Test ranges
    discounts = [10, 15, 20, 25, 30, 35, 40]
    durations = [7, 14, 21, 28]
    
    results = []
    
    # Run all scenarios
    for discount in discounts:
        for duration in durations:
            analyzer = PromotionAnalyzer(product, products, business_rules)
            result = analyzer.analyze(discount, duration)
            
            results.append({
                'Discount': f"{discount}%",
                'Duration': f"{duration} days",
                'Net Profit': result['financial']['net_profit'],
                'ROI': result['financial']['roi_pct'],
                'Risk Score': result['risks']['risk_score'],
                'Lift': result['lift']['lift_pct'],
                'Recommendation': result['recommendation']['decision']
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Sort by Net Profit (descending)
    df = df.sort_values('Net Profit', ascending=False)
    
    # Print results
    print("\n📊 ALL SCENARIOS (Sorted by Net Profit):\n")
    print(df.to_string(index=False))
    
    # Find best scenarios
    print("\n" + "=" * 80)
    print("\n🏆 BEST SCENARIOS:\n")
    
    strong_yes = df[df['Recommendation'] == 'Strong Yes']
    if not strong_yes.empty:
        print(f"✅ Found {len(strong_yes)} STRONG YES Recommendations:")
        print(strong_yes.to_string(index=False))
    else:
        print("❌ No 'Strong Yes' scenarios found")
        
        # Show best "Maybe" options
        maybe = df[df['Recommendation'] == 'Maybe']
        if not maybe.empty:
            print(f"\n⚠️ Found {len(maybe)} 'MAYBE' Options:")
            print(maybe.head(3).to_string(index=False))
        else:
            print("\n❌ No 'Maybe' scenarios found either")
            print("\nBest available options:")
            print(df.head(3).to_string(index=False))
    
    print("\n" + "=" * 80)
    
    # Profitability analysis
    print("\n💰 PROFITABILITY INSIGHTS:\n")
    print(f"Best Net Profit: ${df['Net Profit'].max():,.2f}")
    print(f"Worst Net Profit: ${df['Net Profit'].min():,.2f}")
    print(f"Average Net Profit: ${df['Net Profit'].mean():,.2f}")
    
    best_row = df.iloc[0]
    print(f"\n🎯 OPTIMAL COMBINATION:")
    print(f"   Discount: {best_row['Discount']}")
    print(f"   Duration: {best_row['Duration']}")
    print(f"   Expected Net Profit: ${best_row['Net Profit']:,.2f}")
    print(f"   ROI: {best_row['ROI']:.1f}%")
    print(f"   Recommendation: {best_row['Recommendation']}")
    
    return df


def compare_all_products():
    """
    Compare best promotion for each product
    """
    products = data_loader.load_product_catalog()
    business_rules = data_loader.get_business_rules()
    
    print("\n🏪 BEST PROMOTION FOR EACH PRODUCT (20% off, 14 days):")
    print("=" * 100)
    
    results = []
    
    for product in products:
        # Test a standard 20% off for 14 days
        analyzer = PromotionAnalyzer(product, products, business_rules)
        result = analyzer.analyze(20, 14)
        
        results.append({
            'Product': product['name'],
            'Category': product['category'],
            'Net Profit': result['financial']['net_profit'],
            'ROI': result['financial']['roi_pct'],
            'Recommendation': result['recommendation']['decision']
        })
    
    df = pd.DataFrame(results)
    df = df.sort_values('Net Profit', ascending=False)
    
    print(df.to_string(index=False))
    
    print("\n" + "=" * 100)
    
    strong_yes_count = len(df[df['Recommendation'] == 'Strong Yes'])
    maybe_count = len(df[df['Recommendation'] == 'Maybe'])
    
    print(f"\n✅ Products with 'Strong Yes': {strong_yes_count}")
    print(f"⚠️ Products with 'Maybe': {maybe_count}")
    
    if strong_yes_count > 0:
        print("\n✅ 'Strong Yes' Products:")
        strong_yes = df[df['Recommendation'] == 'Strong Yes']
        print(strong_yes.to_string(index=False))


if __name__ == "__main__":
    # Test specific product
    print("\n" + "=" * 80)
    print("PRICE SENSE AI - SCENARIO OPTIMIZER")
    print("=" * 80)
    
    # Example: Test first product (or specify prod_001 for Almonds)
    products = data_loader.load_product_catalog()
    if products:
        first_product_id = products[0]['id']
        test_all_scenarios(first_product_id)
        
        # Compare all products
        print("\n\n")
        compare_all_products()
    else:
        print("❌ No products found. Check your data files.")
