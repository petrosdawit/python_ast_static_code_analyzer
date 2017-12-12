import string
import os
from collections import defaultdict

class T9Input(object):
    
    def __init__(self, dictionary_file):
        self.whole_number_to_text = defaultdict(set)
        self.text_representation = {}
        # '''    
        # For creating the dictionary of text_representation of (key: letter, value: integer) I iterate through
        # the string.ascii_lowercase and increment by 3 each time. I check if the first index of the pair i
        # is w or p, and increment i by once more for that special case. I also start my number at 2
        # '''
        num = 2
        i = 0
        while i < len(string.ascii_lowercase):
            self.text_representation[string.ascii_lowercase[i]] = str(num)
            self.text_representation[string.ascii_lowercase[i+1]] = str(num)
            self.text_representation[string.ascii_lowercase[i+2]] = str(num)            
            if string.ascii_lowercase[i] == 'p' or string.ascii_lowercase[i] == 'w':                
                self.text_representation[string.ascii_lowercase[i+3]] = str(num)
                i += 1
            i += 3
            num += 1
        self.read_input(dictionary_file)
            
    def read_input(self, filename):
        with open(filename, 'r') as wordfile:
            for word in wordfile.read().splitlines():
                if self.check_valid_word(word):
                    text_number = self.convert_to_text(word.lower())
                    self.whole_number_to_text[text_number].add(word.lower())
        
    def convert_to_text(self, word):
        num_representation = []
        for char in word:
            num_representation.append(self.text_representation[char])
        return ''.join(num_representation)
        
    def check_valid_word(self, word):
        for char in word:
            if ('A' <= char and char <= 'Z') or ('a' <= char and char <= 'z'):
                continue
            return False
        return True
    
    def check_valid_string_int(self, word):
        for char in word:
            if '2' <= char <= '9':
                continue
            return False
        return True
    
    def test_sample_input(self, testfile):
        with open(testfile, 'r') as wordtestfile:
            for word in wordtestfile.read().splitlines():
                if self.check_valid_string_int(word):
                    if word in self.whole_number_to_text:
                        string_output = []
                        for char in self.whole_number_to_text[word]:
                            string_output.append(char)
                        print('{} : {}'.format(word, ','.join(string_output)))
                    else:
                        print('{} : {}'.format(word, '<No Results>'))
                else:
                    print('{} : {}'.format('Not a valid integer text representation', word))
                    
    def run_test_cases(self, dir):
        for filename in os.listdir(dir):
            print('Testing file input:', filename)
            self.test_sample_input(os.path.join(dir,filename))
            
    def repeat_dictionary(self, dir):
        for filename in os.listdir(dir):
            print('Testing file input:', filename)
            self.read_input(os.path.join(dir,filename))
            self.test_sample_input('repeat.txt')
            
                        
if __name__ == '__main__':
    T9 = T9Input('dictionary.txt')
    T9.run_test_cases('test_files')
    # T9.repeat_dictionary('dictionary_test_files')
    

    