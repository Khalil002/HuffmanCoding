import os
import sys
import time
import heapq
import pickle

class HuffmanCompressor:
	def __init__(self, input_path, output_path):
		self.input_path = input_path
		self.output_path = output_path
		self.heap = []
		self.codes = {}
		self.reverse_mapping = {}

	class HeapNode:
		def __init__(self, char, freq):
			self.char = char
			self.freq = freq
			self.left = None
			self.right = None

		def __lt__(self, other):
			if(other == None):
				return False
			return self.freq < other.freq

		def __eq__(self, other):
			if(other == None):
				return False
			return self.freq == other.freq

	def create_freq_table(self, text):
		freq_table = {}
		for character in text:
			if not character in freq_table:
				freq_table[character] = 0
			freq_table[character] += 1
		return freq_table

	def create_heap(self, freq_table):
		for key in freq_table:
			node = self.HeapNode(key, freq_table[key])
			heapq.heappush(self.heap, node)

	def merge_nodes(self):
		while(len(self.heap)>1):
			node1 = heapq.heappop(self.heap)
			node2 = heapq.heappop(self.heap)

			merged = self.HeapNode(None, node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2

			heapq.heappush(self.heap, merged)

	def create_codes_helper(self, root, current_code):
		if(root == None):
			return

		if(root.char != None):
			self.codes[root.char] = current_code
			self.reverse_mapping[current_code] = root.char
			return

		self.create_codes_helper(root.left, current_code + "0")
		self.create_codes_helper(root.right, current_code + "1")

	def create_codes(self):
		root = heapq.heappop(self.heap)
		current_code = ""
		self.create_codes_helper(root, current_code)

	def get_encoded_text(self, text):
		encoded_text = ""
		for character in text:
			encoded_text += self.codes[character]
		return encoded_text

	def pad_encoded_text(self, encoded_text):
		extra_padding = 8 - len(encoded_text) % 8
		for i in range(extra_padding):
			encoded_text += "0"

		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text

	def get_byte_array(self, padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		for i in range(0, len(padded_encoded_text), 8):
			byte = padded_encoded_text[i:i+8]
			b.append(int(byte, 2))
		return b

	def compress(self):
		with open(self.input_path, 'r+') as input_file, open(self.output_path, 'wb') as output_file:
			text = input_file.read()

			freq_table = self.create_freq_table(text)
			self.create_heap(freq_table)
			self.merge_nodes()
			self.create_codes()

			encoded_text = self.get_encoded_text(text)
			padded_encoded_text = self.pad_encoded_text(encoded_text)

			b = self.get_byte_array(padded_encoded_text)
			b2 = pickle.dumps(self.reverse_mapping)
			b3 = len(b2)
			b4 = b3.to_bytes(4, sys.byteorder)
			
			#writes the pickled reverse_mapping length
			output_file.write(b4)

			#writes the pickled reverse_mapping
			output_file.write(b2)

			#writes the compressed file
			output_file.write(bytes(b))
	
	#def save_reverse_mapping(self):
	#	with open('reverse_mapping', 'wb') as reverse_mapping_file:
	#		pickle.dump(self.reverse_mapping, reverse_mapping_file)

def main():
	input_path = sys.argv[1]
	output_path = "comprimido.elmejorprofesor"
	if(os.path.isfile(input_path) == False):
		print(input_path+" does not exist")
		exit(0)
	hc = HuffmanCompressor(input_path, output_path)

	st = time.time()
	hc.compress()
	et = time.time()
	ft = et-st
	print("Tiempo de compresión: "+str(ft)+" segundos")

	input_size = os.path.getsize(input_path)
	output_size = os.path.getsize(output_path)
	compression_ratio = output_size/input_size*100
	print("Índice de compresión: "+str(compression_ratio)+"%")

	#hc.save_reverse_mapping()

if __name__ == "__main__":
    main()