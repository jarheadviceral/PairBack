"""PairBack: Coding Assignment 2 backend data-structure demonstration.
Python 3.9+; no third-party packages. Run normally for demo, --test for tests.
"""
import sys
import unittest
from dataclasses import dataclass


class ArrayList:
    """Resizable array: explicit size, capacity, indexing and copying.

    Python lists provide fixed allocated slots here. Growth is implemented
    explicitly rather than delegated to list.append().
    """
    def __init__(self):
        self.capacity = 2
        self._size = 0
        self._data = [None] * self.capacity

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        if not isinstance(index, int) or not 0 <= index < self._size:
            raise IndexError("Index outside stored records")
        return self._data[index]

    def __iter__(self):
        for i in range(self._size):
            yield self._data[i]

    def append(self, value):
        if self._size == self.capacity:
            self.capacity *= 2
            larger = [None] * self.capacity
            for i in range(self._size):
                larger[i] = self._data[i]
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


class UndoStack:
    """Explicit LIFO structure backed by our ArrayList."""
    def __init__(self):
        self._items = ArrayList()

    def __len__(self):
        return len(self._items)

    def isEmpty(self):
        return len(self) == 0

    def push(self, change):
        self._items.append(change)

    def peek(self):
        return None if self.isEmpty() else self._items[len(self) - 1]

    def pop(self):
        return None if self.isEmpty() else self._items.pop_last()


@dataclass
class Report:
    report_id: str
    description: str
    status: str = "available"


class PairBack:
    def __init__(self):
        self.records = ArrayList()
        self.history = UndoStack()

    def find(self, report_id):
        # Linear lookup is sufficient for this data-structure milestone.
        for report in self.records:
            if report.report_id == report_id:
                return report
        return None

    def add(self, report_id, description):
        report_id, description = report_id.strip(), description.strip()
        if not report_id or not description:
            raise ValueError("ID and description are required")
        if self.find(report_id):
            raise ValueError("Duplicate report ID")
        self.records.append(Report(report_id, description))

    def release(self, report_id):
        report = self.find(report_id)
        if report is None:
            return "Report not found"
        if report.status == "released":
            return "Already released; no history entry added"
        # Staff must verify ownership before calling this operation.
        self.history.push((report.report_id, report.status))
        report.status = "released"
        return "Released " + report_id

    def undo(self):
        change = self.history.pop()
        if change is None:
            return "Nothing to undo"
        report_id, previous_status = change
        self.find(report_id).status = previous_status
        return "Restored " + report_id + " to " + previous_status

    def show(self):
        print(f"Records={len(self.records)}, capacity={self.records.capacity}")
        for report in self.records:
            print(f"  {report.report_id}: {report.description} [{report.status}]")
        print(f"Undo depth={len(self.history)}, top={self.history.peek()}")


def demo():
    app = PairBack()
    print("PAIRBACK | Array-based list and Undo stack")
    print("Synthetic found-item records; ownership verification is external.\n")
    for record in [("F001", "Blue bottle"), ("F002", "Black umbrella"),
                   ("F003", "Red notebook")]:
        app.add(*record)
    print("1. Add three records: capacity grows from 2 to 4")
    app.show()
    print("\n2. Release two verified items: push two changes")
    print(app.release("F001"))
    print(app.release("F002"))
    app.show()
    print("\n3. Undo: F002 is restored first (Last-In, First-Out)")
    print(app.undo())
    app.show()
    print("\n4. Undo remaining change, then try an empty stack")
    print(app.undo())
    print(app.undo())
    print("\n5. Add more data: capacity grows again")
    app.add("F004", "White charger")
    app.add("F005", "Green pouch")
    app.show()
    print("\n6. Invalid operations are handled")
    print(app.release("UNKNOWN"))
    try:
        app.add("F001", "Duplicate")
    except ValueError as error:
        print(error)


class Tests(unittest.TestCase):
    def test_array_growth_and_order(self):
        a = ArrayList()
        for i in range(1000):
            a.append(i)
        self.assertEqual(list(a), list(range(1000)))
        self.assertGreaterEqual(a.capacity, 1000)
        for i in reversed(range(1000)):
            self.assertEqual(a.pop_last(), i)
        with self.assertRaises(IndexError):
            a.pop_last()

    def test_index_bounds(self):
        a = ArrayList()
        for index in [-1, 0, 10]:
            with self.assertRaises(IndexError):
                a[index]

    def test_stack_growth_lifo_and_peek(self):
        s = UndoStack()
        self.assertIsNone(s.pop())
        self.assertIsNone(s.peek())
        for i in range(1000):
            s.push(i)
        self.assertEqual(s.peek(), 999)
        self.assertEqual(len(s), 1000)
        for i in reversed(range(1000)):
            self.assertEqual(s.pop(), i)
        self.assertTrue(s.isEmpty())

    def test_release_undo_and_invalid_operations(self):
        a = PairBack()
        a.add("F1", "Bottle")
        a.add("F2", "Bottle")  # Duplicate descriptions are allowed.
        for args in [("F1", "Other"), (" ", "Bottle"), ("F3", " ")]:
            with self.assertRaises(ValueError):
                a.add(*args)
        a.release("missing")
        self.assertEqual(len(a.history), 0)
        a.release("F1")
        a.release("F1")
        a.release("F2")
        self.assertEqual(len(a.history), 2)
        a.undo()
        self.assertEqual(a.find("F2").status, "available")
        self.assertEqual(a.find("F1").status, "released")
        a.undo()
        self.assertEqual(a.find("F1").status, "available")
        self.assertEqual(a.undo(), "Nothing to undo")


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        demo()
