import time


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
    def is_a_match(search_part, look_ahead_part):
        if search_part <= look_ahead_part:
            for i in range(len(look_ahead_part)):
                if search_part[i % len(search_part)] != look_ahead_part[i]:
                    return False
            return True
        return False
        # return all(search_part[i % len(search_part)] == look_ahead_part[i] for i in range(len(look_ahead_part)))

    @staticmethod
    def compress(search_buffer_len=1, look_ahead_buffer_len=1, string=None,  input_file=None, output_file=None):
        if not string and input_file:
            with open(input_file, 'rb') as input_f:
                string = input_f.read()
                string.rstrip()
        compressed_string = []
        cursor = 0
        START = 0
        END = 1
        search_buffer = (-search_buffer_len, 0)
        look_ahead_buffer = (cursor, look_ahead_buffer_len)
        output_binary = bytearray()
        while True:
            found = False
            match = string[search_buffer[START] if search_buffer[END] > search_buffer_len else 0:search_buffer[END]]
            parts = LZ77Compressor.get_substrings_with_offset_of(match)
            for i, chars_match in enumerate(parts):
                char_built = string[look_ahead_buffer[START]:look_ahead_buffer[END]]
                for _ in string[look_ahead_buffer[START]:look_ahead_buffer[END]]:
                    if char_built == chars_match["string"]\
                            or LZ77Compressor.is_a_match(chars_match["string"], char_built)\
                            and chars_match["offset"] == len(chars_match["string"]):
                        found = True
                        next_char_index = look_ahead_buffer[START] + len(char_built)\
                            if look_ahead_buffer[START] + len(char_built) < len(string) else None

                        compressed_string.append(LZ77Compressor.Triple(chars_match["offset"],
                                                                       len(char_built),
                                                                       string[next_char_index] if next_char_index
                                                                       else None))
                        if output_file:
                            output_binary.extend(chars_match["offset"].to_bytes(length=1, byteorder="big"))
                            output_binary.extend(len(char_built).to_bytes(length=1, byteorder="big"))
                            output_binary.append(string[next_char_index] if next_char_index else 0)
                        break
                    char_built = char_built[:-1]
                if found:
                    break
            if not found:
                compressed_string.append(LZ77Compressor.Triple(0, 0, string[cursor]))
                if output_file:
                    output_binary.extend((0).to_bytes(length=1, byteorder="big"))
                    output_binary.extend((0).to_bytes(length=1, byteorder="big"))
                    output_binary.append(string[cursor])

            triple = compressed_string[len(compressed_string) - 1]
            # print(triple.offset, triple.length, triple.char)
            offset = triple.length + 1
            look_ahead_buffer = look_ahead_buffer[START] + offset, look_ahead_buffer[END] + offset \
                if look_ahead_buffer[END] + offset < len(string) - 1 else len(string)
            search_buffer = search_buffer[START] + offset, search_buffer[END] + offset
            cursor = look_ahead_buffer[START]
            progress = search_buffer[END]/((len(string) - 1)/100)
            print("progress: {:.3f}".format(progress), flush=True)
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

    @staticmethod
    def decompress_binary(input_file, output_file):
        cursor = -1
        decompressed_string = bytearray()
        with open(input_file, 'rb') as input_f:
            compressed_binary = input_f.read()
        print(len(compressed_binary))
        j = 0
        i = 3
        OFFSET = 0
        LENGTH = 1
        CHAR = 2
        while True:
            print(compressed_binary[j:i])
            triple = compressed_binary[j:i]
            offset = triple[OFFSET]
            length = triple[LENGTH]
            char = triple[CHAR]
            print(offset, length, char)
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
            j += 3
            i += 3
            if i > len(compressed_binary):
                break
        if output_file:
            with open(output_file, 'wb') as output_f:
                output_f.write(decompressed_string)
        return decompressed_string


def main():
    start = time.time()
    compressor = LZ77Compressor()
    # file_name = "fields.c"
    # with open(file_name, 'rb') as input_f:
    #     data = input_f.read()
    #     data.rstrip()
    # print(data)
    # compressed_file = compressor.compress(search_buffer_len=255, look_ahead_buffer_len=150, input_file=file_name,
    #                                       output_file="compressed.txt")
    # print(compressed_file)
    # decompressed_file = compressor.decompress_binary(input_file="compressed.txt", output_file="decompressed.txt")
    # print(decompressed_file)
    # print(data == decompressed_file)
    print(compressor.decompress(compressor.compress(10, 10, "arman arman")))
    end = time.time()
    print("Time elapsed:", end - start)


main()

