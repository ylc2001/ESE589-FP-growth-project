"""
FP-Growth Algorithm Implementation for Frequent Itemset Mining

This module implements the FP-growth algorithm which efficiently mines frequent itemsets
without candidate generation using a compressed FP-tree data structure.
"""

from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional


class FPNode:
    """A node in the FP-tree."""
    
    def __init__(self, item: str, count: int = 1, parent: Optional['FPNode'] = None):
        """
        Initialize an FP-tree node.
        
        Args:
            item: The item stored in this node
            count: The count/support of this item
            parent: The parent node
        """
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.next = None  # Link to next node with same item
    
    def increment(self, count: int = 1):
        """Increment the count of this node."""
        self.count += count


class FPTree:
    """FP-tree data structure for efficient frequent pattern mining."""
    
    def __init__(self, transactions: List[List[str]], min_support: int, root_item: Optional[str] = None):
        """
        Build an FP-tree from transactions.
        
        Args:
            transactions: List of transactions (each transaction is a list of items)
            min_support: Minimum support threshold
            root_item: Item label for root (used in conditional FP-trees)
        """
        self.min_support = min_support
        self.root = FPNode(root_item if root_item else 'root', 0)
        self.header_table = {}  # Maps item -> (count, first_node)
        
        # Count item frequencies
        item_counts = Counter()
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        # Filter items by min_support and sort by frequency (descending)
        self.frequent_items = {item: count for item, count in item_counts.items() 
                              if count >= min_support}
        
        # Build FP-tree
        for transaction in transactions:
            # Filter and sort transaction by frequency
            sorted_items = [item for item in transaction 
                           if item in self.frequent_items]
            sorted_items.sort(key=lambda x: self.frequent_items[x], reverse=True)
            
            if sorted_items:
                self._insert_transaction(sorted_items, self.root)
    
    def _insert_transaction(self, items: List[str], node: FPNode):
        """
        Insert a transaction into the FP-tree.
        
        Args:
            items: Sorted list of items in the transaction
            node: Current node in the tree
        """
        if not items:
            return
        
        item = items[0]
        
        # If child exists, increment its count
        if item in node.children:
            node.children[item].increment()
        else:
            # Create new child node
            new_node = FPNode(item, 1, node)
            node.children[item] = new_node
            
            # Update header table
            if item in self.header_table:
                # Link to existing nodes with same item
                current = self.header_table[item][1]
                while current.next:
                    current = current.next
                current.next = new_node
            else:
                self.header_table[item] = (self.frequent_items[item], new_node)
        
        # Recursively insert remaining items
        if len(items) > 1:
            self._insert_transaction(items[1:], node.children[item])
    
    def get_paths(self, item: str) -> List[Tuple[List[str], int]]:
        """
        Get all paths ending with the given item.
        
        Args:
            item: The item to find paths for
            
        Returns:
            List of (path, count) tuples where path is a list of items
        """
        paths = []
        
        if item not in self.header_table:
            return paths
        
        # Follow the node links
        node = self.header_table[item][1]
        while node:
            path = []
            parent = node.parent
            
            # Trace back to root
            while parent and parent.item != 'root' and parent.item is not None:
                path.append(parent.item)
                parent = parent.parent
            
            if path:
                paths.append((path[::-1], node.count))
            
            node = node.next
        
        return paths


def fp_growth(transactions: List[List[str]], min_support: int, 
              prefix: Optional[List[str]] = None) -> Dict[Tuple[str, ...], int]:
    """
    FP-Growth algorithm for mining frequent itemsets.
    
    Args:
        transactions: List of transactions (each transaction is a list of items)
        min_support: Minimum support threshold (absolute count)
        prefix: Current itemset prefix (used in recursion)
    
    Returns:
        Dictionary mapping frequent itemsets (as tuples) to their support counts
    """
    if prefix is None:
        prefix = []
    
    # Build FP-tree
    tree = FPTree(transactions, min_support)
    
    if not tree.frequent_items:
        return {}
    
    # Mine patterns
    patterns = {}
    
    # Sort items by frequency (ascending) for bottom-up mining
    items = sorted(tree.header_table.items(), key=lambda x: x[1][0])
    
    for item, (count, _) in items:
        # Create new pattern
        new_pattern = prefix + [item]
        patterns[tuple(new_pattern)] = count
        
        # Get conditional pattern base
        conditional_patterns = tree.get_paths(item)
        
        if conditional_patterns:
            # Build conditional transactions
            conditional_transactions = []
            for path, path_count in conditional_patterns:
                for _ in range(path_count):
                    conditional_transactions.append(path)
            
            # Recursively mine conditional FP-tree
            conditional_patterns_dict = fp_growth(
                conditional_transactions, 
                min_support, 
                new_pattern
            )
            patterns.update(conditional_patterns_dict)
    
    return patterns


def mine_frequent_itemsets(transactions: List[List[str]], 
                           min_support: float = 0.01) -> Dict:
    """
    Main function to mine frequent itemsets.
    
    Args:
        transactions: List of transactions (each transaction is a list of items)
        min_support: Minimum support threshold (as fraction of total transactions)
    
    Returns:
        Dictionary containing:
        - 'frequent_itemsets': Dict mapping itemsets to support
        - 'num_transactions': Total number of transactions
    """
    num_transactions = len(transactions)
    min_support_count = int(min_support * num_transactions)
    
    # Mine frequent itemsets
    patterns = fp_growth(transactions, min_support_count)
    
    result = {
        'frequent_itemsets': patterns,
        'num_transactions': num_transactions,
        'min_support': min_support,
        'min_support_count': min_support_count
    }
    
    return result


if __name__ == "__main__":
    # Simple test example
    transactions = [
        ['bread', 'milk'],
        ['bread', 'diaper', 'beer', 'eggs'],
        ['milk', 'diaper', 'beer', 'cola'],
        ['bread', 'milk', 'diaper', 'beer'],
        ['bread', 'milk', 'diaper', 'cola']
    ]
    
    print("Testing FP-Growth Algorithm")
    print("=" * 50)
    print(f"Number of transactions: {len(transactions)}")
    print(f"Transactions: {transactions}")
    print()
    
    result = mine_frequent_itemsets(transactions, min_support=0.4)
    
    print(f"Minimum support: {result['min_support']} ({result['min_support_count']} transactions)")
    print(f"\nFrequent Itemsets ({len(result['frequent_itemsets'])} found):")
    for itemset, support in sorted(result['frequent_itemsets'].items(), key=lambda x: (-len(x[0]), -x[1])):
        print(f"  {set(itemset)}: {support}")
