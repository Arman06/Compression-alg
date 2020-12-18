class SA:
    @staticmethod
    def naive(string):
        suffixes = []
        while string:
            suffixes.append(string)
            string = string[1:]
        return suffixes, sorted(range(len(suffixes)), key=lambda index: suffixes[index])

    @staticmethod
    def lcp(string, suf_arr=None, suf_arr_indices=None):
        if suf_arr is None or suf_arr_indices is None:
            suf_arr, suf_arr_indices = SA.naive(string)
        lcp_arr = [0]
        j = suf_arr_indices[0]
        for i in suf_arr_indices[1:]:
            common_ch_sum = 0
            for ch1, ch2 in zip(suf_arr[i], suf_arr[j]):
                if ch1 == ch2:
                    common_ch_sum += 1
                else:
                    break
            lcp_arr.append(common_ch_sum)
            j = i
        return lcp_arr

    @staticmethod
    def uniq_substrings_count(string):
        lcp = SA.lcp(string)
        return int((len(string) * (len(string) + 1) / 2) - sum(lcp))

    @staticmethod
    def lcs(string1, string2, special_char="#"):
        concatenated = string1 + special_char + string2
        sa, sa_i = SA.naive(concatenated)
        lcp = SA.lcp(concatenated, sa, sa_i)
        max_sub = 0
        max_sub_i = -1
        for i, prefix_l in enumerate(lcp):
            if prefix_l > max_sub:
                if not(special_char in sa[sa_i[i]] and special_char in sa[sa_i[i - 1]]):
                    max_sub = prefix_l
                    max_sub_i = sa_i[i]
        if max_sub > 0:
            if sa[max_sub_i][0:max_sub] in string1 and sa[max_sub_i][0:max_sub] in string2:
                return sa[max_sub_i][0:max_sub]
        return False

    @staticmethod
    def matching(word, pattern):
        if len(word) >= len(pattern):
            for i in range(len(pattern)):
                if pattern[i] != word[i]:
                    return False
            return True
        return False

    @staticmethod
    def matching_with_repetition(word, pattern):
        char_built = ""
        i = 0
        while char_built != word:
            found = True
            char_built += word[i]
            i += 1
            for j in range(len(pattern)):
                if char_built[j % len(char_built)] != pattern[j]:
                    found = False
                    break
            if found:
                return True
        return False

    @staticmethod
    def binary_search_matching(array, value):
        l = 0
        r = len(array) - 1
        mid = (l + r) // 2
        while l <= r:
            if SA.matching(array[mid], value):
                return mid
            if array[mid] > value:
                r = mid - 1
                mid = (l + r) // 2
                continue
            if array[mid] < value:
                l = mid + 1
                mid = (l + r) // 2
                continue

    @staticmethod
    def pattern_search(string, pattern):
        sa, sa_i = SA.naive(string)
        suffix_array = [sa[i] for i in sa_i]
        pattern_index = SA.binary_search_matching(suffix_array, pattern)
        if pattern_index:
            return len(string) - sa_i[pattern_index]
        else:
            return False

