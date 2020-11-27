

class LZ77Compressor:
    class Triple:
        def __init__(self, offset, length, char):
            self.offset = offset
            self.length = length
            self.char = char

        def __str__(self):
            return "offset: {}, length: {}, character: {}".format(self.offset, self.length, self.char)

        def __repr__(self):
            return "(offset: {}, length: {}, character: {})".format(self.offset, self.length, self.char)

    @staticmethod
    def get_substrings_with_offset_of(string):
        sub_strings = []
        start = 0
        end = len(string)
        while start - end != 0:
            for start2, end2 in zip(range(start + 1, 0, -1), range(end, 0, -1)):
                sub_strings.append({"string": string[start2 - 1:end2], "offset": end + 1 - start2})
            start += 1
        return sub_strings

    @staticmethod
    def compress(string, search_buffer_len=1, look_ahead_buffer_len=1):
        compressed_string = []
        cursor = 0
        START = 0
        END = 1
        search_buffer = (-search_buffer_len, 0)
        look_ahead_buffer = (cursor, look_ahead_buffer_len)
        while True:
            found = False
            print(search_buffer, look_ahead_buffer)
            match = string[search_buffer[START] if search_buffer[END] > search_buffer_len else 0:search_buffer[END]]
            parts = LZ77Compressor.get_substrings_with_offset_of(match)
            print(parts)
            for i, chars_match in enumerate(parts):
                char_built = ""
                for j, char1 in enumerate(string[look_ahead_buffer[START]:look_ahead_buffer[END]]):
                    char_built += char1
                    print(chars_match["string"], char_built)
                    if char_built == chars_match["string"]:
                        found = True
                        print("found")
                        print(chars_match["offset"])
                        next_char_index = look_ahead_buffer[START] + len(chars_match["string"])\
                            if look_ahead_buffer[START] + len(chars_match["string"]) < len(string) else None
                        compressed_string.append(LZ77Compressor.Triple(chars_match["offset"],
                                                                       len(chars_match["string"]),
                                                                       string[next_char_index] if next_char_index
                                                                       else None))
                        break
                if found:
                    break
            if not found:
                compressed_string.append(LZ77Compressor.Triple(0, 0, string[cursor]))
            triple = compressed_string[len(compressed_string) - 1]
            print(triple.offset, triple.length, triple.char)
            offset = triple.length + 1
            print()
            look_ahead_buffer = look_ahead_buffer[START] + offset, look_ahead_buffer[END] + offset
            search_buffer = search_buffer[START] + offset, search_buffer[END] + offset
            cursor = look_ahead_buffer[START]
            if search_buffer[END] > len(string) - 1:
                break
        return compressed_string

    @staticmethod
    def decompress(compressed_string):
        cursor = -1
        decompressed_string = ""
        for triple in compressed_string:
            if triple.offset == 0 and triple.length == 0:
                decompressed_string += triple.char
                cursor += 1
            else:
                cursor -= triple.offset - 1
                decompressed_string += decompressed_string[cursor:cursor + triple.length]
                if triple.char:
                    decompressed_string += triple.char
                cursor = len(decompressed_string) - 1
        return decompressed_string


def main():
    compressor = LZ77Compressor()
    compressed_string1 = compressor.compress("abcabaabc", 3, 3)
    print(compressed_string1)
    compressed_string = compressor.compress("AABCBBABC", 6, 3)
    print(compressed_string)
    print(compressor.decompress(compressed_string))
    print(compressor.decompress(compressed_string1))


main()

