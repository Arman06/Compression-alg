from math import log2, acos, sqrt, pi, tan
import turtle


class ListNew(list):
    @property
    def last_index(self):
        return len(self) - 1

    def __gt__(self, other):
        return len(self) > other


class PriorityQueue:
    def __init__(self, items=[]):
        self.contents = ListNew()
        for item in items:
            self.contents.append(item)
            self.heapify_up()

    def __bool__(self):
        return bool(self.contents)

    @property
    def last(self):
        return self.contents.last_index

    def last_element(self):
        return self.contents[self.last]

    @staticmethod
    def left_child(i):
        return 2 * i + 1

    @staticmethod
    def right_child(i):
        return 2 * i + 2

    @staticmethod
    def parent(i):
        return (i - 1)//2

    def heapify_up(self):
        new = self.last
        while new >= 1:
            parent = self.parent(new)
            if self.contents[new] < self.contents[parent]:
                self.contents[new], self.contents[parent] = self.contents[parent], self.contents[new]
                new = parent
            else:
                return

    def search(self, node):
        return self.contents.index(node)

    def insert(self, item):
        self.contents.append(item)
        self.heapify_up()

    def delete(self, node=None):
        if node is None:
            root = self.contents[0]
            self.contents[0], self.contents[self.last] = self.contents[self.last], self.contents[0]
            self.contents.pop()
            self.heapify_down()
            return root
        else:
            index = self.search(node)
            self.contents[index], self.contents[self.last] = self.contents[self.last], self.contents[index]
            self.contents.pop()
            self.heapify_down(index)

    def heapify_down(self, index=0):
        mini = index
        while index < len(self.contents):
            left = self.left_child(index)
            right = self.right_child(index)
            if left < len(self.contents) and right < len(self.contents):
                if self.contents[right] < self.contents[left]:
                    min_child_index = right
                else:
                    min_child_index = left
                if self.contents[min_child_index] <= self.contents[index]:
                    mini = min_child_index
            elif left < len(self.contents):
                if self.contents[left] <= self.contents[index]:
                    mini = left
            if index == mini:
                return
            self.contents[index], self.contents[mini] = self.contents[mini], self.contents[index]
            index = mini

    def peek(self):
        return self.contents[0]


class HuffmanTree:
    class Node:
        def __init__(self, value=None, probability=None, l_child=None, r_child=None):
            self.value = value
            self.probability = probability
            self.l_child = l_child
            self.r_child = r_child

        def __eq__(self, other):
            return self.probability == other

        def __lt__(self, other):
            return self.probability < other

        def __le__(self, other):
            return self.probability <= other

        def __gt__(self, other):
            return self.probability > other

        def __ge__(self, other):
            return self.probability >= other

    def __init__(self):
        self.root = None

    def huffman_coding(self, symbols):
        queue = PriorityQueue()
        for symbol, frequency in symbols:
            queue.insert(self.Node(value=symbol, probability=frequency))
        while queue.contents > 1:
            # for node in queue.contents:
            #     print(node.value, node.probability, end=" ")
            # print()
            node1 = queue.delete()
            node2 = queue.delete()
            parent_node = self.Node(value=None, probability=(node1.probability + node2.probability),
                                    l_child=node2, r_child=node1)
            queue.insert(parent_node)
        self.root = queue.delete()
        return self.root

    def _get_code(self, cur_node, code="", codes_array=[]):

        if cur_node is not None:
            if cur_node.value is not None:
                codes_array.append((cur_node.value, code))
            if cur_node.l_child is not None:
                code += "0"
                self._get_code(cur_node.l_child, code, codes_array)
            code = code[:-1]
            if cur_node.r_child is not None:
                code += "1"
                self._get_code(cur_node.r_child, code, codes_array)
        return codes_array

    def get_codes(self):
        if self.root is not None:
            return sorted(self._get_code(self.root), key=lambda pair: pair[0])

    @staticmethod
    def entropy(symbols):
        return -sum([probability * log2(probability) for symbol, probability in symbols])

    @staticmethod
    def average_len(codes, symbols):
        return sum([probability[1] * len(symbol[1]) for symbol, probability in zip(codes, symbols)])

    def _draw(self, cur_node, pen, origin, floors):
        if cur_node is not None:
            pen.penup()
            pen.setposition(origin)
            pen.pendown()
            if cur_node.value is not None:
                pen.write(cur_node.value)
            else:
                pen.write("{:0.2f}".format(cur_node.probability))
            node_dist = 32
            distance = node_dist * sqrt((1 + ((2 ** abs(floors) * 13) ** 2)/(5*node_dist**2)))
            # distance = sqrt(42*log2(abs(floors**2))/(0.34*5))
            angle = 180/pi * acos(node_dist/distance)
            if cur_node.l_child is not None:
                pen.setposition(origin)
                # turtle.pendown()
                pen.right(angle)
                pen.forward(distance)
                left = pen.position()
                pen.left(angle)
                if cur_node.l_child is not None:
                    self._draw(cur_node.l_child, pen, left, floors - 0.85)
            if cur_node.r_child is not None:
                pen.penup()
                pen.setposition(origin)
                pen.pendown()
                pen.left(angle)
                pen.forward(distance)
                right = pen.position()
                pen.right(angle)
                if cur_node.r_child is not None:
                    self._draw(cur_node.r_child, pen, right, floors - 0.85)

    def draw(self, alphabet):
        if self.root is not None:
            pen = turtle.Turtle()
            pen.hideturtle()
            pen.speed(1)
            pen.setheading(-90)
            pen.penup()
            pen.goto(0, 260)
            pen.pendown()
            turtle.Screen().screensize(900, 900)
            self._draw(self.root, pen, pen.position(), sqrt(len(alphabet)))

def main():

    huf = HuffmanTree()
    # source = [("a_1", 0.25), ("a_2", 0.25), ("a_3", 0.125), ("a_4", 0.125),
    #                     ("a_5", 0.125), ("a_6", 0.0625), ("a_7", 0.0625)]

    source = [("а", 0.064), ("б", 0.015), ("в", 0.039), ("г", 0.014),
                ("д", 0.026), ("е ё ", 0.074), ("ж", 0.008),
               ("з", 0.015), ("и", 0.064), ("й", 0.010), ("к", 0.029),
                ("л", 0.036), ("м", 0.026), ("н", 0.056),
               ("о", 0.096), ("п", 0.024), ("р", 0.041), ("с", 0.047),
               ("т", 0.056), ("у ", 0.021), ("ф", 0.020), ("х", 0.009),
               ("ц", 0.004), ("ч", 0.013), ("ш", 0.006),  ("щ ", 0.003),
               ("ъ ь", 0.015), ("ы", 0.016),  ("э ", 0.003), ("ю", 0.007), ("я", 0.019), ("-", 0.124)
               ]

    # source = [("a_1", 0.4), ("a_2", 0.15), ("a_3", 0.15), ("a_4", 0.15), ("a_5", 0.15)]

    # huf.huffman_coding([("a_1", 0.4), ("a_2", 0.15), ("a_3", 0.15), ("a_4", 0.15), ("a_5", 0.15)])
    # print(huf.entropy([("a_1", 0.4), ("a_2", 0.15), ("a_3", 0.15), ("a_4", 0.15), ("a_5", 0.15)]))
    huf.huffman_coding(source)
    print("entropy is " + str(HuffmanTree.entropy(source)) + " bits")
    array_of_codes = huf.get_codes()
    print(HuffmanTree.average_len(array_of_codes, source))
    print("array of codes:", array_of_codes)
    huf.draw(source)
    turtle.done()


main()
