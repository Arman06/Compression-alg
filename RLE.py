class RLE:
    @staticmethod
    def encoding(string):
        encoded_string = ""
        i = 0
        char = string[0]
        for ch in string:
            if ch == char:
                i += 1
            else:
                encoded_string += str(i) + char
                char = ch
                i = 1
        encoded_string += (str(i) + char)
        return encoded_string

    @staticmethod
    def decode(encoded_string):
        decoded_string = ""
        for repetitions, char in zip(encoded_string[::2], encoded_string[1::2]):
            for rep in range(int(repetitions)):
                decoded_string += char
        return decoded_string


def main():
    string = "Teeeeeest striiiiing fooooor thiiiis algorithm of compresssssssion"
    print("Initial string:", string)
    encoded_string = RLE.encoding(string)
    print("Encoded string:", encoded_string)
    decoded_string = RLE.decode(encoded_string)
    print("Decoded string:", decoded_string)
    print("Are they the same?", string == decoded_string)


main()

