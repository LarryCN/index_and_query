import config

class listnode:
    def __init__(self, value):
        self.val = value
        self.next = None
        self.pre = None

class LRU:
    def __init__(self):
        self.max_n = config.CACHE_SIZE / config.CACHE_BLOCK
        self.n = 0
        self.cache = {}
        self.head = listnode(-1)
        self.tail = listnode(-2)
        self.tail.pre = self.head
        self.head.next = self.tail

    def get(self, key):
        if key in self.cache:
            result = self.cache[key][0]
            node = self.cache[key][1]
            node.next.pre = node.pre
            node.pre.next = node.next
            self.head.next.pre = node
            node.next = self.head.next
            node.pre = self.head
            self.head.next = node
            return result
        else:
            return -1

    def set(self, key, data):
        if self.n < self.max_n:
            node = listnode(key)
            node.next = self.head.next
            node.next.pre = node
            node.pre = self.head
            self.head.next = node
            self.cache[key] = [data, node]
            self.n += 1
        else:
            node = self.tail.pre
            self.tail.pre = node.pre
            node.pre.next = self.tail
            self.cache.pop(node.val)
            node.val = key
            self.cache[key] = [data, node]
            node.next = self.head.next
            node.next.pre = node
            node.pre = self.head
            self.head.next = node

