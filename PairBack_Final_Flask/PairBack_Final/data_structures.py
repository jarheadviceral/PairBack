"""PairBack's student-implemented data structures and algorithms."""
class ArrayList:
    """Resizable array with explicit size/capacity and indexed access."""
    def __init__(self, values=None):
        self.capacity = 2
        self._size = 0
        self._data = [None] * self.capacity
        if values:
            for value in values:
                self.append(value)

    def __len__(self): return self._size
    def __iter__(self):
        for i in range(self._size): yield self._data[i]
    def __getitem__(self, index):
        if not isinstance(index, int) or index < 0 or index >= self._size:
            raise IndexError("Index outside stored records")
        return self._data[index]

    def append(self, value):
        if self._size == self.capacity:
            self.capacity *= 2
            larger = [None] * self.capacity
            for i in range(self._size): larger[i] = self._data[i]
            self._data = larger
        self._data[self._size] = value
        self._size += 1

    def pop_last(self):
        if self._size == 0: raise IndexError("Array is empty")
        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None
        return value

    def to_list(self): return [self._data[i] for i in range(self._size)]


class UndoStack:
    """Explicit LIFO stack backed by PairBack's ArrayList."""
    def __init__(self): self._items = ArrayList()
    def __len__(self): return len(self._items)
    def isEmpty(self): return len(self) == 0
    def push(self, change): self._items.append(change)
    def peek(self): return None if self.isEmpty() else self._items[len(self)-1]
    def pop(self): return None if self.isEmpty() else self._items.pop_last()


def merge_sort(items, key):
    """Recursive merge sort; stable ordering; returns a new Python list."""
    if len(items) <= 1: return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:]); merged.extend(right[j:])
    return merged


def binary_search(sorted_records, target_id):
    """Iterative binary search over records sorted by report_id."""
    low, high = 0, len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        current = sorted_records[mid]["report_id"]
        if current == target_id: return sorted_records[mid]
        if current < target_id: low = mid + 1
        else: high = mid - 1
    return None
