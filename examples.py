"""
Complete example demonstrating the FP-Growth algorithm implementation.

This script shows:
1. Basic usage with small example
2. Mining frequent itemsets
3. Generating association rules
4. Working with different parameters
"""

from fp_growth import mine_frequent_itemsets


def example_1_basic_usage():
    """Example 1: Basic FP-growth usage with small dataset."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)
    
    # Simple grocery store transactions
    transactions = [
        ['bread', 'milk'],
        ['bread', 'diaper', 'beer', 'eggs'],
        ['milk', 'diaper', 'beer', 'cola'],
        ['bread', 'milk', 'diaper', 'beer'],
        ['bread', 'milk', 'diaper', 'cola']
    ]
    
    print("\nTransactions:")
    for i, transaction in enumerate(transactions, 1):
        print(f"  {i}. {transaction}")
    
    # Mine frequent itemsets with 40% minimum support
    result = mine_frequent_itemsets(transactions, min_support=0.4)
    
    print(f"\nMinimum Support: 40% (>= {result['min_support_count']} transactions)")
    print(f"Found {len(result['frequent_itemsets'])} frequent itemsets\n")
    
    # Display results grouped by size
    by_size = {}
    for itemset, support in result['frequent_itemsets'].items():
        size = len(itemset)
        if size not in by_size:
            by_size[size] = []
        by_size[size].append((set(itemset), support))
    
    for size in sorted(by_size.keys()):
        print(f"{size}-itemsets:")
        for itemset, support in sorted(by_size[size], key=lambda x: -x[1]):
            support_pct = (support / len(transactions)) * 100
            print(f"  {itemset}: support={support} ({support_pct:.0f}%)")
        print()


def example_2_association_rules():
    """Example 2: Generating association rules."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Association Rules")
    print("="*70)
    
    # Market basket transactions
    transactions = [
        ['milk', 'bread', 'butter'],
        ['beer', 'bread'],
        ['milk', 'bread', 'butter', 'beer'],
        ['milk', 'bread', 'butter'],
        ['bread', 'butter'],
        ['milk', 'bread', 'butter', 'eggs'],
        ['milk', 'bread'],
        ['beer', 'chips'],
        ['milk', 'butter', 'bread', 'chips'],
        ['milk', 'bread', 'butter']
    ]
    
    print(f"\nTransactions: {len(transactions)}")
    for i, transaction in enumerate(transactions[:5], 1):
        print(f"  {i}. {transaction}")
    print("  ...")
    
    # Mine with association rules
    result = mine_frequent_itemsets(
        transactions,
        min_support=0.3,      # 30% minimum support
        min_confidence=0.7,   # 70% minimum confidence
        return_rules=True
    )
    
    print(f"\nMinimum Support: 30%")
    print(f"Minimum Confidence: 70%")
    print(f"Frequent Itemsets: {len(result['frequent_itemsets'])}")
    print(f"Association Rules: {len(result['rules'])}")
    
    # Display top rules
    print("\nTop Association Rules:")
    for i, (antecedent, consequent, confidence, support) in enumerate(result['rules'][:10], 1):
        print(f"\n  {i}. {antecedent} => {consequent}")
        print(f"     Confidence: {confidence:.1%} (If someone buys {antecedent},")
        print(f"                         they buy {consequent} {confidence:.1%} of the time)")
        print(f"     Support: {support} transactions")


def example_3_parameter_comparison():
    """Example 3: Effect of different support thresholds."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Effect of Support Threshold")
    print("="*70)
    
    # Generate a larger synthetic dataset
    import random
    random.seed(42)
    
    items = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    transactions = []
    
    for _ in range(100):
        # Random transaction size between 2 and 5
        size = random.randint(2, 5)
        # More common items have higher probability
        weights = [0.3, 0.3, 0.2, 0.1, 0.05, 0.03, 0.01, 0.01]
        transaction = []
        while len(transaction) < size:
            item = random.choices(items, weights=weights)[0]
            if item not in transaction:
                transaction.append(item)
        transactions.append(transaction)
    
    print(f"\nGenerated {len(transactions)} transactions")
    print(f"Example transactions: {transactions[:3]}")
    
    # Test different support values
    support_values = [0.05, 0.10, 0.20, 0.30]
    
    print("\nResults for different support thresholds:")
    print(f"{'Support':<10} {'Min Count':<12} {'Itemsets Found':<15} {'Execution Time':<15}")
    print("-" * 60)
    
    import time
    for min_support in support_values:
        start = time.time()
        result = mine_frequent_itemsets(transactions, min_support=min_support)
        elapsed = time.time() - start
        
        min_count = result['min_support_count']
        num_itemsets = len(result['frequent_itemsets'])
        
        print(f"{min_support:<10.2f} {min_count:<12} {num_itemsets:<15} {elapsed:<15.4f}s")


def example_4_real_world_scenario():
    """Example 4: Realistic e-commerce scenario."""
    print("\n" + "="*70)
    print("EXAMPLE 4: E-Commerce Product Recommendations")
    print("="*70)
    
    # Realistic product transactions
    transactions = [
        ['laptop', 'mouse', 'keyboard'],
        ['laptop', 'mouse', 'laptop_bag'],
        ['mouse', 'keyboard'],
        ['laptop', 'mouse', 'keyboard', 'laptop_bag', 'usb_hub'],
        ['tablet', 'tablet_case', 'stylus'],
        ['laptop', 'mouse', 'laptop_bag'],
        ['keyboard', 'mouse'],
        ['laptop', 'keyboard', 'mouse', 'webcam'],
        ['tablet', 'tablet_case'],
        ['laptop', 'mouse', 'keyboard', 'laptop_bag'],
        ['mouse', 'keyboard', 'mousepad'],
        ['laptop', 'laptop_bag'],
        ['tablet', 'stylus', 'tablet_case'],
        ['laptop', 'mouse', 'keyboard'],
        ['keyboard', 'mouse', 'usb_hub']
    ]
    
    print(f"\nE-commerce transactions: {len(transactions)}")
    print("Sample transactions:")
    for i, transaction in enumerate(transactions[:5], 1):
        print(f"  {i}. {transaction}")
    
    # Mine patterns for product recommendations
    result = mine_frequent_itemsets(
        transactions,
        min_support=0.2,      # 20% support
        min_confidence=0.6,   # 60% confidence
        return_rules=True
    )
    
    print(f"\nFrequent Product Combinations (>= 20% support):")
    
    # Filter for 2+ item sets
    combos = [(set(itemset), support) 
              for itemset, support in result['frequent_itemsets'].items() 
              if len(itemset) >= 2]
    combos.sort(key=lambda x: -x[1])
    
    for itemset, support in combos[:10]:
        support_pct = (support / len(transactions)) * 100
        print(f"  {itemset}: {support_pct:.0f}% of customers")
    
    print(f"\nProduct Recommendation Rules (>= 60% confidence):")
    for i, (antecedent, consequent, confidence, support) in enumerate(result['rules'][:8], 1):
        print(f"\n  {i}. If customer buys: {antecedent}")
        print(f"     Recommend: {consequent}")
        print(f"     Confidence: {confidence:.1%}")
        print(f"     (Based on {support} transactions)")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("FP-GROWTH ALGORITHM - COMPLETE EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates the FP-Growth algorithm implementation")
    print("with various real-world scenarios and use cases.")
    
    # Run all examples
    example_1_basic_usage()
    example_2_association_rules()
    example_3_parameter_comparison()
    example_4_real_world_scenario()
    
    print("\n" + "="*70)
    print("✓ All examples completed!")
    print("="*70)
    print("\nFor more information:")
    print("  - Run 'python validate.py' to see validation tests")
    print("  - Run 'python run_benchmark.py' for comprehensive benchmarks")
    print("  - See README.md for detailed documentation")


if __name__ == "__main__":
    main()
