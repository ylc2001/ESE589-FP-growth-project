"""
FP-Growth Algorithm Implementation for Frequent Itemset Mining

This module implements the FP-growth algorithm which efficiently mines frequent itemsets
without candidate generation using a compressed FP-tree data structure.
"""

from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
import sys


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
    
    def get_memory_size(self) -> int:
        """
        Get approximate memory size of this node in bytes.
        
        Returns:
            Approximate memory size in bytes
        """
        # Size of the object itself
        size = sys.getsizeof(self)
        # Add size of item string
        size += sys.getsizeof(self.item)
        # Add size of count integer
        size += sys.getsizeof(self.count)
        # Add size of children dict
        size += sys.getsizeof(self.children)
        return size


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
        
        # Memory and structure tracking
        self.num_nodes = 1  # Start with root node
        self.max_depth = 0
        
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
                self._insert_transaction(sorted_items, self.root, depth=0)
    
    def _insert_transaction(self, items: List[str], node: FPNode, depth: int = 0):
        """
        Insert a transaction into the FP-tree.
        
        Args:
            items: Sorted list of items in the transaction
            node: Current node in the tree
            depth: Current depth in the tree
        """
        if not items:
            return
        
        # Update max depth tracking
        self.max_depth = max(self.max_depth, depth + 1)
        
        item = items[0]
        
        # If child exists, increment its count
        if item in node.children:
            node.children[item].increment()
        else:
            # Create new child node
            new_node = FPNode(item, 1, node)
            node.children[item] = new_node
            self.num_nodes += 1  # Track node count
            
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
            self._insert_transaction(items[1:], node.children[item], depth + 1)
    
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
    
    def get_tree_stats(self) -> Dict:
        """
        Get statistics about the FP-tree structure.
        
        Returns:
            Dictionary containing tree statistics
        """
        # Calculate total memory size by traversing the tree
        total_memory = self._calculate_tree_memory(self.root)
        
        return {
            'num_nodes': self.num_nodes,
            'max_depth': self.max_depth,
            'num_frequent_items': len(self.frequent_items),
            'num_header_entries': len(self.header_table),
            'memory_bytes': total_memory,
            'memory_kb': total_memory / 1024,
            'memory_mb': total_memory / (1024 * 1024)
        }
    
    def _calculate_tree_memory(self, node: FPNode) -> int:
        """
        Recursively calculate memory size of the tree.
        
        Args:
            node: Current node
            
        Returns:
            Total memory size in bytes
        """
        size = node.get_memory_size()
        for child in node.children.values():
            size += self._calculate_tree_memory(child)
        return size


def fp_growth(transactions: List[List[str]], min_support: int, 
              prefix: Optional[List[str]] = None,
              track_memory: bool = False) -> Tuple[Dict[Tuple[str, ...], int], Dict]:
    """
    FP-Growth algorithm for mining frequent itemsets.
    
    Args:
        transactions: List of transactions (each transaction is a list of items)
        min_support: Minimum support threshold (absolute count)
        prefix: Current itemset prefix (used in recursion)
        track_memory: Whether to track memory statistics
    
    Returns:
        Tuple of (patterns dictionary, memory_stats dictionary)
        - patterns: Dictionary mapping frequent itemsets (as tuples) to their support counts
        - memory_stats: Dictionary with memory tracking information
    """
    if prefix is None:
        prefix = []
    
    # Initialize memory tracking
    memory_stats = {
        'total_trees_created': 0,
        'max_tree_nodes': 0,
        'max_tree_depth': 0,
        'total_tree_memory_bytes': 0
    }
    
    # Build FP-tree
    tree = FPTree(transactions, min_support)
    
    # Track tree statistics
    if track_memory:
        tree_stats = tree.get_tree_stats()
        memory_stats['total_trees_created'] = 1
        memory_stats['max_tree_nodes'] = tree_stats['num_nodes']
        memory_stats['max_tree_depth'] = tree_stats['max_depth']
        memory_stats['total_tree_memory_bytes'] = tree_stats['memory_bytes']
    
    if not tree.frequent_items:
        return {}, memory_stats
    
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
            conditional_patterns_dict, conditional_memory = fp_growth(
                conditional_transactions, 
                min_support, 
                new_pattern,
                track_memory
            )
            patterns.update(conditional_patterns_dict)
            
            # Aggregate memory statistics
            if track_memory:
                memory_stats['total_trees_created'] += conditional_memory['total_trees_created']
                memory_stats['max_tree_nodes'] = max(
                    memory_stats['max_tree_nodes'], 
                    conditional_memory['max_tree_nodes']
                )
                memory_stats['max_tree_depth'] = max(
                    memory_stats['max_tree_depth'], 
                    conditional_memory['max_tree_depth']
                )
                memory_stats['total_tree_memory_bytes'] += conditional_memory['total_tree_memory_bytes']
    
    return patterns, memory_stats


def mine_frequent_itemsets(transactions: List[List[str]], 
                           min_support: float = 0.01,
                           track_memory: bool = False) -> Dict:
    """
    Main function to mine frequent itemsets.
    
    Args:
        transactions: List of transactions (each transaction is a list of items)
        min_support: Minimum support threshold (as fraction of total transactions)
        track_memory: Whether to track memory consumption metrics
    
    Returns:
        Dictionary containing:
        - 'frequent_itemsets': Dict mapping itemsets to support
        - 'num_transactions': Total number of transactions
        - 'memory_stats': Memory consumption statistics (if track_memory=True)
    """
    import tracemalloc
    
    num_transactions = len(transactions)
    min_support_count = int(min_support * num_transactions)
    
    # Start memory tracking if requested
    if track_memory:
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
    
    # Mine frequent itemsets
    patterns, tree_memory_stats = fp_growth(transactions, min_support_count, track_memory=track_memory)
    
    # Get peak memory usage
    if track_memory:
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_stats = {
            'peak_memory_bytes': peak_memory,
            'peak_memory_kb': peak_memory / 1024,
            'peak_memory_mb': peak_memory / (1024 * 1024),
            'current_memory_bytes': current_memory,
            'memory_used_bytes': peak_memory - start_memory,
            'memory_used_kb': (peak_memory - start_memory) / 1024,
            'memory_used_mb': (peak_memory - start_memory) / (1024 * 1024),
            'tree_stats': tree_memory_stats
        }
    else:
        memory_stats = None
    
    result = {
        'frequent_itemsets': patterns,
        'num_transactions': num_transactions,
        'min_support': min_support,
        'min_support_count': min_support_count
    }
    
    if track_memory:
        result['memory_stats'] = memory_stats
    
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
