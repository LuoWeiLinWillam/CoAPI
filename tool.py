# coding=utf-8
import subprocess
import time
import re
import os
import sys
import threading

def clear_data(pattern,file_path):
	input=[]
	for line in open(file_path):
		line = line.strip()
		if len(line)==0:continue
		
		words = re.findall(pattern,line)
		words = filter(lambda x: x!='',words)

		input.append(words)
	return input

def write_ncnf(output_file_path, index, block, result, output_partial_order):
	f = file(output_file_path, 'w+')

	for key in index:
		f.writelines('m ' + str(index[key]) + ' = ' + key + '\n')
	f.writelines('c\n')

	for key in block:
		f.writelines('b ' + str(key) + ' ' + str(block[key][0]) + ' ' + str(block[key][1]) + '\n')
	f.writelines('c\n')

	f.writelines(output_partial_order)
	f.writelines('c\n')

	f.writelines('p cnf ' + ' ' + str(len(index)) + ' ' + str(len(result)) + '\n')
	for line in result:
		words = line.split(' ')
		if (len(words) == 2) & (int(words[0]) == index['r1']):
			f.writelines('-' + line + '\n')
		else:
			f.writelines(line + '\n')
	f.writelines('0\n')
	
	f.close()

def write_pcnf(output_file_path, index, block, result ,output_partial_order):
	f = file(output_file_path, 'w+')

	for key in index:
		f.writelines('m ' + str(index[key]) + ' = ' + key + '\n')
	f.writelines('c\n')

	for key in block:
		f.writelines('b ' + str(key) + ' ' + str(block[key][0]) + ' ' + str(block[key][1]) + '\n')
	f.writelines('c\n')

	f.writelines(output_partial_order)
	f.writelines('c\n')

	f.writelines('p cnf ' + ' ' + str(len(index)) + ' ' + str(len(result)) + '\n')
	for line in result:
		words = line.split(' ')
		f.writelines(line + '\n')
	f.writelines('0\n')
	
	f.close()

def write_pcnf_normalize(output_file_path, result, num_all_var, num_ori_var):
	f = file(output_file_path, 'w+')

	f.writelines('c n orig vars ' + str(num_ori_var) + '\n')

	f.writelines('p cnf ' + str(num_all_var) + ' ' + str(len(result)) + '\n')
	for line in result:
		words = line.split(' ')
		f.writelines(line + '\n')
	# f.writelines('0\n')
	
	f.close()

def write_ncnf_normalize(output_file_path, result, num_all_var, num_ori_var):
	f = file(output_file_path, 'w+')

	f.writelines('c n orig vars ' + str(num_ori_var) + '\n')

	f.writelines('p cnf ' + str(num_all_var) + ' ' + str(len(result)) + '\n')
	for line in result:
		words = line.split(' ')
		if (len(words) == 2):
			f.writelines('-' + line + '\n')
		else:
			f.writelines(line + '\n')
	# f.writelines('0\n')
	
	f.close()