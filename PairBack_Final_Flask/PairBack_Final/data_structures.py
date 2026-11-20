"""Student-implemented data structures and algorithms for PairBack."""


class ArrayList:
    """Resizable array with explicit size, capacity, and indexed access."""

    def __init__(self, values=None):
        self.capacity = 2
        self._size = 0
        self._data = [None] * self.capacity
        if values:
            for value in values:
                self.append(value)

    def __len__(self):
        return self._size

    def __iter__(self):
        for index in range(self._size):
            yield self._data[index]

    def __getitem__(self, index):
        if not isinstance(index, int) or index < 0 or index >= self._size:
            raise IndexError("Index outside stored records")
        return self._data[index]

    def append(self, value):
        if self._size == self.capacity:
            self.capacity *= 2
            larger = [None] * self.capacity
            for index in range(self._size):
                larger[index] = self._data[index]
            self._data = larger
        self._data[self._size] = value
        self._size += 1

    def pop_last(self):
        if self._size == 0:
            raise IndexError("Array is empty")
        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None
        return value

    def to_list(self):
        return [self._data[index] for index in range(self._size)]


class UndoStack:
    """LIFO stack backed by PairBack's ArrayList."""

    def __init__(self):
        self._items = ArrayList()

    def __len__(self):
        return len(self._items)

    def is_empty(self):
        return len(self) == 0

    def push(self, change):
        self._items.append(change)

    def peek(self):
        return None if self.is_empty() else self._items[len(self) - 1]

    def pop(self):
        return None if self.is_empty() else self._items.pop_last()


def quick_sort(items, key):
    """Return a new list ordered with iterative three-way Quick Sort.

    The middle element is used as the pivot. Equal keys are kept together,
    which avoids unnecessary partitions when many records share a key. An
    explicit stack replaces Python recursion so an unfavorable pivot sequence
    cannot fail at the interpreter's recursion limit.
    """
    values = list(items)
    if len(values) <= 1:
        return values

    partitions = [(0, len(values) - 1)]
    while partitions:
        low, high = partitions.pop()

        # Continue with the smaller side and save the larger side. This keeps
        # the explicit stack small even when partitions are unbalanced.
        while low < high:
            pivot_key = key(values[(low + high) // 2])
            lower = low
            current = low
            higher = high

            # Dutch-national-flag partition: [< pivot][= pivot][> pivot].
            while current <= higher:
                current_key = key(values[current])
                if current_key < pivot_key:
                    values[lower], values[current] = (
                        values[current],
                        values[lower],
                    )
                    lower += 1
                    current += 1
                elif current_key > pivot_key:
                    values[current], values[higher] = (
                        values[higher],
                        values[current],
                    )
                    higher -= 1
                else:
                    current += 1

            left = (low, lower - 1)
            right = (higher + 1, high)
            left_size = left[1] - left[0] + 1
            right_size = right[1] - right[0] + 1

            if left_size < right_size:
                if right[0] < right[1]:
                    partitions.append(right)
                low, high = left
            else:
                if left[0] < left[1]:
                    partitions.append(left)
                low, high = right

    return values


def insertion_sort(items, higher_priority):
    """Stable priority ordering without changing the caller's collection.

    Best case O(k), average/worst case O(k^2). The returned copy uses O(k)
    space; the insertion loop itself uses O(1) auxiliary space.
    """
    ordered = list(items)
    for index in range(1, len(ordered)):
        current = ordered[index]
        position = index - 1
        while position >= 0 and higher_priority(current, ordered[position]):
            ordered[position + 1] = ordered[position]
            position -= 1
        ordered[position + 1] = current
    return ordered
