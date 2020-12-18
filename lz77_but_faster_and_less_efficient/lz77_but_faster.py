import time
from Suffix_array import SA
from math import log2, ceil


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

    def __init__(self, search_buffer_len=5, look_ahead_buffer_len=5):
        self.search_buffer_len = search_buffer_len
        self.look_ahead_buffer_len = look_ahead_buffer_len

    @staticmethod
    def from_bytes_to_string(b_string):
        return ''.join(chr(b) for b in b_string)

    @staticmethod
    def from_string_to_bytes(string, encoding="UTF-8"):
        return bytes(string, encoding=encoding)

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
    def is_a_match(search_part, look_ahead_part):
        if search_part <= look_ahead_part:
            for i in range(len(look_ahead_part)):
                if search_part[i % len(search_part)] != look_ahead_part[i]:
                    return False
            return True
        return False
        # return all(search_part[i % len(search_part)] == look_ahead_part[i] for i in range(len(look_ahead_part)))

    def compress(self, string=None,  input_file=None, output_file=None):
        if not string and input_file:
            with open(input_file, 'rb') as input_f:
                string = input_f.read()
                string.rstrip()
        compressed_string = []
        cursor = 0
        START = 0
        END = 1
        search_buffer = (-self.search_buffer_len, 0)
        look_ahead_buffer = (cursor, self.look_ahead_buffer_len)
        number_chunk_length = 1 if ceil(log2(self.look_ahead_buffer_len)/8) < 1\
            else ceil(log2(self.look_ahead_buffer_len)/8)
        output_binary = bytearray()
        while True:
            search_buffer_string = string[search_buffer[START] if search_buffer[END] > self.search_buffer_len
                                          else 0:search_buffer[END]]
            look_ahead_buffer_string = string[look_ahead_buffer[START]:look_ahead_buffer[END]]
            print("Search buffer ", search_buffer_string, "    |    ", "Look ahead buffer", look_ahead_buffer_string)
            # match = SA.lcs(LZ77Compressor.from_bytes_to_string(search_buffer_string),
            #                LZ77Compressor.from_bytes_to_string(look_ahead_buffer_string))
            pattern = string[look_ahead_buffer[START]:look_ahead_buffer[END]]
            if len(pattern) == 0:
                break
            pattern_built = chr(pattern[0])
            best_pattern_len = 0
            k = 1
            best_match_distance = False
            while k < len(pattern):
                match_distance = SA.pattern_search(LZ77Compressor.from_bytes_to_string(search_buffer_string),
                                                   pattern_built)
                if not match_distance:
                    break
                best_match_distance = match_distance
                best_pattern_len = len(pattern_built)
                pattern_built += chr(pattern[k])
                k += 1
            match_distance = best_match_distance
            if match_distance:
                next_char_index = look_ahead_buffer[START] + best_pattern_len \
                    if look_ahead_buffer[START] + best_pattern_len < len(string) else None
                match_offset = match_distance
                compressed_string.append(LZ77Compressor.Triple(match_offset,
                                                               best_pattern_len,
                                                               string[next_char_index] if next_char_index
                                                               else None))
                if output_file:
                    output_binary.extend(match_offset.to_bytes(length=number_chunk_length, byteorder="big"))
                    output_binary.extend(best_pattern_len.to_bytes(length=number_chunk_length, byteorder="big"))
                    output_binary.append(string[next_char_index] if next_char_index else 0)
            else:
                compressed_string.append(LZ77Compressor.Triple(0, 0, string[cursor]))
                if output_file:
                    output_binary.extend((0).to_bytes(length=number_chunk_length, byteorder="big"))
                    output_binary.extend((0).to_bytes(length=number_chunk_length, byteorder="big"))
                    output_binary.append(string[cursor])

            triple = compressed_string[len(compressed_string) - 1]
            print("<", triple.offset, triple.length, chr(triple.char), ">")
            print()
            offset = triple.length + 1
            look_ahead_buffer = look_ahead_buffer[START] + offset, look_ahead_buffer[END] + offset \
                if look_ahead_buffer[END] + offset < len(string) - 1 else len(string)
            search_buffer = search_buffer[START] + offset, search_buffer[END] + offset
            cursor = look_ahead_buffer[START]
            progress = search_buffer[END]/((len(string) - 1)/100)
            # print("progress: {:.3f}".format(progress), flush=True)
            if search_buffer[END] > len(string) - 1:
                break
        if output_file:
            with open(output_file, 'wb') as output_f:
                output_f.write(output_binary)
            return output_binary
        else:
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
                decompressed_parts = decompressed_string[cursor:cursor + triple.offset]
                for i in range(triple.length):
                    decompressed_string += decompressed_parts[i % len(decompressed_parts)]
                if triple.char:
                    decompressed_string += triple.char
                cursor = len(decompressed_string) - 1
        return decompressed_string

    def decompress_binary(self, input_file, output_file):
        cursor = -1
        decompressed_string = bytearray()
        with open(input_file, 'rb') as input_f:
            compressed_binary = input_f.read()
        print(len(compressed_binary))
        single_number_chunk_length = 1 if ceil(log2(self.look_ahead_buffer_len)/8) < 1\
            else ceil(log2(self.look_ahead_buffer_len)/8)
        number_chunk_length = single_number_chunk_length * 2
        OFFSET = slice(0, single_number_chunk_length)
        LENGTH = slice(single_number_chunk_length, number_chunk_length)
        CHAR = number_chunk_length
        CHUNK_SIZE = number_chunk_length + 1
        print("CHUNK SIZE:", CHUNK_SIZE)
        j = 0
        i = CHUNK_SIZE
        while True:
            print(compressed_binary[j:i])
            triple = compressed_binary[j:i]
            offset = int.from_bytes(triple[OFFSET], byteorder='big')
            length = int.from_bytes(triple[LENGTH], byteorder='big')
            char = triple[CHAR]
            print(offset, length, chr(char))
            if offset == 0 and length == 0:
                decompressed_string.append(triple[CHAR])
                cursor += 1
            else:
                cursor -= offset - 1
                decompressed_parts = decompressed_string[cursor:cursor + offset]
                for k in range(length):
                    decompressed_string.append(decompressed_parts[k % len(decompressed_parts)])
                if char:
                    decompressed_string.append(char)

                cursor = len(decompressed_string) - 1
            j += CHUNK_SIZE
            i += CHUNK_SIZE
            if i > len(compressed_binary):
                break
        if output_file:
            print("to output", decompressed_string)
            with open(output_file, 'wb') as output_f:
                output_f.write(decompressed_string)
        return decompressed_string


def main():
    start = time.time()
    compressor = LZ77Compressor(search_buffer_len=255, look_ahead_buffer_len=255)
    file_name = "plrabn12.txt"
    with open(file_name, 'rb') as input_f:
        data = input_f.read()
        data.rstrip()
    print(data)
    compressed_file = compressor.compress(input_file=file_name, output_file="compressed.txt")
    print(compressed_file[0:4])
    decompressed_file = compressor.decompress_binary(input_file="compressed.txt", output_file="decompressed.txt")
    print(data)
    print(decompressed_file)
    print(data == decompressed_file)
    end = time.time()
    print("Time elapsed:", end - start)


main()

