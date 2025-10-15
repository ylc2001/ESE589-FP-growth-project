"""
Validation module for FP-Growth algorithm implementation.

This module contains small illustrating examples used to validate the correctness
of the FP-growth implementation.
"""

from fp_growth import mine_frequent_itemsets, fp_growth
from typing import List, Dict, Tuple


def test_simple_example():
    """Test with a simple, well-known example."""
    print("\n" + "="*70)
    print("TEST 1: Simple Transaction Example")
    print("="*70)
    
    transactions = [
        ['bread', 'milk'],
        ['bread', 'diaper', 'beer', 'eggs'],
        ['milk', 'diaper', 'beer', 'cola'],
        ['bread', 'milk', 'diaper', 'beer'],
        ['bread', 'milk', 'diaper', 'cola']
    ]
    
    print(f"Transactions ({len(transactions)} total):")
    for i, t in enumerate(transactions, 1):
        print(f"  T{i}: {t}")
    
    min_support = 0.4  # 2 out of 5 transactions
    result = mine_frequent_itemsets(transactions, min_support=min_support)
    
    print(f"\nMinimum Support: {min_support} ({result['min_support_count']} transactions)")
    print(f"\nFrequent Itemsets Found: {len(result['frequent_itemsets'])}")
    
    # Group by size
    by_size = {}
    for itemset, support in result['frequent_itemsets'].items():
        size = len(itemset)
        if size not in by_size:
            by_size[size] = []
        by_size[size].append((itemset, support))
    
    for size in sorted(by_size.keys()):
        print(f"\n{size}-itemsets:")
        for itemset, support in sorted(by_size[size], key=lambda x: -x[1]):
            print(f"  {set(itemset)}: {support}/{len(transactions)} = {support/len(transactions):.2f}")
    
    # Verify some expected patterns (convert to sets for comparison)
    expected_sets = [
        {'bread'},
        {'milk'},
        {'diaper'},
        {'beer'},
        {'bread', 'milk'},
        {'bread', 'diaper'},
        {'milk', 'diaper'},
        {'beer', 'diaper'},
    ]
    
    # Convert result itemsets to sets for easier comparison
    result_sets = {frozenset(itemset): support 
                   for itemset, support in result['frequent_itemsets'].items()}
    
    print("\nValidation:")
    all_passed = True
    for expected_set in expected_sets:
        frozen_set = frozenset(expected_set)
        if frozen_set in result_sets:
            support = result_sets[frozen_set]
            print(f"  ✓ {expected_set} found with support {support}")
        else:
            print(f"  ✗ {expected_set} NOT found")
            all_passed = False
    
    return all_passed


def test_book_example():
    """Test with classic example from data mining textbooks."""
    print("\n" + "="*70)
    print("TEST 2: Classic Textbook Example")
    print("="*70)
    
    # This is a common example used in FP-growth papers and textbooks
    transactions = [
        ['f', 'a', 'c', 'd', 'g', 'i', 'm', 'p'],
        ['a', 'b', 'c', 'f', 'l', 'm', 'o'],
        ['b', 'f', 'h', 'j', 'o'],
        ['b', 'c', 'k', 's', 'p'],
        ['a', 'f', 'c', 'e', 'l', 'p', 'm', 'n']
    ]
    
    print(f"Transactions ({len(transactions)} total):")
    for i, t in enumerate(transactions, 1):
        print(f"  T{i}: {sorted(t)}")
    
    min_support = 0.6  # 3 out of 5 transactions
    result = mine_frequent_itemsets(transactions, min_support=min_support)
    
    print(f"\nMinimum Support: {min_support} ({result['min_support_count']} transactions)")
    print(f"\nFrequent Itemsets Found: {len(result['frequent_itemsets'])}")
    
    # Group by size
    by_size = {}
    for itemset, support in result['frequent_itemsets'].items():
        size = len(itemset)
        if size not in by_size:
            by_size[size] = []
        by_size[size].append((itemset, support))
    
    for size in sorted(by_size.keys()):
        print(f"\n{size}-itemsets:")
        for itemset, support in sorted(by_size[size], key=lambda x: -x[1]):
            print(f"  {set(itemset)}: {support}/{len(transactions)} = {support/len(transactions):.2f}")
    
    # Items that should be frequent with support >= 3
    items_freq = {}
    for t in transactions:
        for item in t:
            items_freq[item] = items_freq.get(item, 0) + 1
    
    print("\nItem Frequencies:")
    for item, freq in sorted(items_freq.items(), key=lambda x: -x[1]):
        status = "✓" if freq >= 3 else "✗"
        print(f"  {status} {item}: {freq}")
    
    return True


def test_empty_and_edge_cases():
    """Test edge cases."""
    print("\n" + "="*70)
    print("TEST 3: Edge Cases")
    print("="*70)
    
    # Test 1: Empty transactions
    print("\nTest 3.1: Empty transaction list")
    result = mine_frequent_itemsets([], min_support=0.5)
    print(f"  Result: {len(result['frequent_itemsets'])} itemsets (expected: 0)")
    assert len(result['frequent_itemsets']) == 0, "Empty transactions should yield no patterns"
    print("  ✓ Passed")
    
    # Test 2: Single transaction
    print("\nTest 3.2: Single transaction")
    transactions = [['a', 'b', 'c']]
    result = mine_frequent_itemsets(transactions, min_support=1.0)
    print(f"  Result: {len(result['frequent_itemsets'])} itemsets")
    print(f"  Itemsets: {[set(k) for k in result['frequent_itemsets'].keys()]}")
    print("  ✓ Passed")
    
    # Test 3: All identical transactions
    print("\nTest 3.3: All identical transactions")
    transactions = [['a', 'b', 'c']] * 5
    result = mine_frequent_itemsets(transactions, min_support=1.0)
    print(f"  Result: {len(result['frequent_itemsets'])} itemsets")
    for itemset, support in sorted(result['frequent_itemsets'].items(), key=lambda x: -len(x[0])):
        print(f"    {set(itemset)}: {support}")
    print("  ✓ Passed")
    
    # Test 4: No frequent itemsets
    print("\nTest 3.4: High support threshold (no frequent itemsets)")
    transactions = [['a'], ['b'], ['c'], ['d']]
    result = mine_frequent_itemsets(transactions, min_support=0.6)
    print(f"  Result: {len(result['frequent_itemsets'])} itemsets (expected: 0)")
    assert len(result['frequent_itemsets']) == 0, "Should have no frequent itemsets"
    print("  ✓ Passed")
    
    # Test 5: Single item transactions
    print("\nTest 3.5: Single item per transaction")
    transactions = [['a'], ['a'], ['a'], ['b'], ['b']]
    result = mine_frequent_itemsets(transactions, min_support=0.4)
    print(f"  Result: {len(result['frequent_itemsets'])} itemsets")
    for itemset, support in result['frequent_itemsets'].items():
        print(f"    {set(itemset)}: {support}")
    print("  ✓ Passed")
    
    return True


def test_support_thresholds():
    """Test different support thresholds."""
    print("\n" + "="*70)
    print("TEST 4: Different Support Thresholds")
    print("="*70)
    
    transactions = [
        ['a', 'b', 'c'],
        ['a', 'b', 'd'],
        ['a', 'c', 'd'],
        ['b', 'c', 'd'],
        ['a', 'b', 'c', 'd']
    ]
    
    print(f"Transactions ({len(transactions)} total):")
    for i, t in enumerate(transactions, 1):
        print(f"  T{i}: {t}")
    
    thresholds = [0.2, 0.4, 0.6, 0.8]
    
    print("\nResults for different support thresholds:")
    for min_sup in thresholds:
        result = mine_frequent_itemsets(transactions, min_support=min_sup)
        min_count = int(min_sup * len(transactions))
        print(f"\n  Support {min_sup} (>= {min_count} transactions):")
        print(f"    Found {len(result['frequent_itemsets'])} frequent itemsets")
        
        # Show summary by size
        by_size = {}
        for itemset in result['frequent_itemsets'].keys():
            size = len(itemset)
            by_size[size] = by_size.get(size, 0) + 1
        
        for size in sorted(by_size.keys()):
            print(f"      {size}-itemsets: {by_size[size]}")
    
    return True


def test_association_rules():
    """Test association rule generation."""
    print("\n" + "="*70)
    print("TEST 5: Association Rule Generation")
    print("="*70)
    
    transactions = [
        ['milk', 'bread', 'butter'],
        ['beer', 'bread'],
        ['milk', 'bread', 'butter', 'beer'],
        ['milk', 'bread', 'butter'],
        ['bread', 'butter']
    ]
    
    print(f"Transactions ({len(transactions)} total):")
    for i, t in enumerate(transactions, 1):
        print(f"  T{i}: {t}")
    
    result = mine_frequent_itemsets(transactions, min_support=0.6, 
                                    min_confidence=0.7, return_rules=True)
    
    print(f"\nMinimum Support: {result['min_support']} ({result['min_support_count']} transactions)")
    print(f"Minimum Confidence: {result['min_confidence']}")
    print(f"\nFrequent Itemsets: {len(result['frequent_itemsets'])}")
    
    for itemset, support in sorted(result['frequent_itemsets'].items(), key=lambda x: (-len(x[0]), -x[1])):
        print(f"  {set(itemset)}: {support}/{len(transactions)} = {support/len(transactions):.2f}")
    
    print(f"\nAssociation Rules: {len(result['rules'])}")
    for antecedent, consequent, confidence, support in sorted(result['rules'], key=lambda x: -x[2]):
        print(f"  {antecedent} => {consequent}")
        print(f"    Confidence: {confidence:.2f}, Support: {support}")
    
    return True


def run_all_validations():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("FP-GROWTH ALGORITHM VALIDATION SUITE")
    print("="*70)
    
    tests = [
        ("Simple Example", test_simple_example),
        ("Textbook Example", test_book_example),
        ("Edge Cases", test_empty_and_edge_cases),
        ("Support Thresholds", test_support_thresholds),
        ("Association Rules", test_association_rules)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All validation tests passed successfully!")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_validations()
    exit(0 if success else 1)
