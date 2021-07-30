# coding=utf-8
import subprocess
import time
import re
import os
import sys
import threading
import gc
import argparse

import compile_prime
import cdnf

WORKSPACE 				= './'
# choose the benchmarks
BENCHMARK 				= 'test/'
# set the limit time
LIMIT_TIME 				= 3600 * 1
LIMIT_MEMORY			= 1000000 * 16

OUTPUT_MOD				= 2
IS_COMPUTE_PIN			= False
IS_COHERENT_OPEN 		= False
IS_UCA_OPEN				= False
IS_QX_OPEN				= False
IS_ZM_OPEN				= False
LIMIT_ITERATION			= 0
BACKTRACK_MOD_CC		= 0
BACKTRACK_MOD_CA		= 1

CompileCover_file_path 	= WORKSPACE + 'Solver/'
CompileAll_file_path 	= WORKSPACE + 'Solver/'
case_input_file_path 	= WORKSPACE + 'example/'
case_output_file_path 	= WORKSPACE + 'example/'
result_output_file_path = WORKSPACE + 'example/output/'

var_index_map 			= {}
index_var_map 			= {}
var_index_dual_rail_map = {}
index_var_dual_rail_map = {}
dag 					= {}
cover_PI 				= []
all_PI 					= []
num_all_PI 				= 0

CompileCover_time 		= 0.0
CompileCover_memory 	= 0
DPLL_time				= 0.0
Extract_time			= 0.0
Backtrack_time			= 0.0
num_API					= 0
times_SAT				= 0
ave_size_API			= 0.0
first_shrink_size 		= 0
second_shrink_size 		= 0
other_shrink_size 		= 0
ave_first_shrink 		= 0.0
ave_second_shrink 		= 0.0
ave_other_shrink 		= 0.0
times_fix_point			= 0
ave_blocker_ignore		= 0.0

CompileAll_time 		= 0.0
CompileAll_memory 		= 0

pi 						= []
min 					= []
fact 					= []
dr 						= []

is_time_out_cover		= False
is_time_out_all			= False
is_memory_out_cover		= False
is_memory_out_all		= False

def clear():
	global var_index_map
	var_index_map = {}
	global index_var_map
	index_var_map = {}
	global var_index_dual_rail_map
	var_index_dual_rail_map = {}
	global index_var_dual_rail_map
	index_var_dual_rail_map = {}
	global dag
	dag = {}
	global cover_PI
	cover_PI = []
	global all_PI
	all_PI = []
	global num_all_PI
	num_all_PI = 0
	global CompileCover_time
	CompileCover_time = 0.0
	global CompileCover_memory
	CompileCover_memory = 0
	global DPLL_time
	DPLL_time = 0.0
	global Extract_time
	Extract_time = 0.0
	global Backtrack_time
	Backtrack_time = 0.0
	global num_API
	num_API = 0
	global times_SAT
	times_SAT = 0
	global ave_size_API
	ave_size_API = 0.0
	global first_shrink_size
	first_shrink_size = 0
	global second_shrink_size
	second_shrink_size = 0
	global other_shrink_size
	other_shrink_size = 0
	global ave_first_shrink
	ave_first_shrink = 0.0
	global ave_second_shrink
	ave_second_shrink = 0.0
	global ave_other_shrink
	ave_other_shrink = 0.0
	global times_fix_point
	times_fix_point = 0
	global ave_blocker_ignore
	ave_blocker_ignore = 0.0
	global CompileAll_time
	CompileAll_time = 0.0
	global CompileAll_memory
	CompileAll_memory = 0
	global pi
	pi = []
	global min
	min = []
	global fact
	fact = []
	global dr
	dr = []
	global is_time_out_cover
	is_time_out_cover = False
	global is_time_out_all
	is_time_out_all	= False
	global is_memory_out_cover
	is_memory_out_cover = False
	global is_memory_out_all
	is_memory_out_all = False

def clean(file_name):

	cnf_path = case_input_file_path + file_name + '/' + file_name + '.cnf'
	ana_path = case_input_file_path + file_name + '/' + file_name + '.ana'
	cpi_path = case_input_file_path + file_name + '/' + file_name + '.cpi'
	# out_path = case_input_file_path + file_name + '/' + file_name + '.out'
	
	if os.path.isfile(cnf_path):
		os.remove(cnf_path)
	if os.path.isfile(ana_path):
		os.remove(ana_path)
	if os.path.isfile(cpi_path):
		os.remove(cpi_path)
	# if os.path.isfile(out_path):
	# 	os.remove(out_path)

def get_info(file_name):
	num_ori_var = 0
	open_file_path = case_input_file_path + file_name + '/' + file_name + '-p.cnf'
	f = open(open_file_path, 'r')

	for line in f:
		if 'c n orig vars' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_ori_var = int(words[0])
			break

	global var_index_map
	global index_var_map
	for i in range(1, num_ori_var + 1):
		var = 'e' + str(i)
		index = i
		var_index_map[var] = index
		index_var_map[index] = var
				
def pncnf2cpi(file_name, is_coherent):

	if IS_COMPUTE_PIN:
		positive_input_file_path = case_input_file_path + file_name + '/' + file_name + '-n.cnf'
		negative_input_file_path = case_input_file_path + file_name + '/' + file_name + '-p.cnf'
	else:
		positive_input_file_path = case_input_file_path + file_name + '/' + file_name + '-p.cnf'
		negative_input_file_path = case_input_file_path + file_name + '/' + file_name + '-n.cnf'

	output_file_path_ana = case_output_file_path + file_name + '/' + file_name + '.ana'

	output_file_path_cpi = case_output_file_path + file_name + '/' + file_name + '.cpi'	
	
	st = compile_prime.compile_cover_NPCNF(CompileCover_file_path, LIMIT_TIME, output_file_path_ana, IS_UCA_OPEN, IS_QX_OPEN, IS_ZM_OPEN, str(LIMIT_ITERATION), str(BACKTRACK_MOD_CC), is_coherent, positive_input_file_path, negative_input_file_path, output_file_path_cpi)

	if st == 2:
		result = []
		result = compile_prime.read_cover_PI(output_file_path_ana, output_file_path_cpi)
		global cover_PI
		cover_PI = result[0]
		global CompileCover_memory
		CompileCover_memory = result[1]
		global CompileCover_time
		CompileCover_time = result[2]
		global DPLL_time
		DPLL_time = result[3]
		global Extract_time
		Extract_time = result[4]
		global Backtrack_time
		Backtrack_time = result[5]
		global num_API
		num_API = result[6]
		global times_SAT
		times_SAT = result[7]
		global ave_size_API
		ave_size_API = result[8]
		global first_shrink_size
		first_shrink_size = result[9]
		global second_shrink_size
		second_shrink_size = result[10]
		global other_shrink_size
		other_shrink_size = result[11]
		global ave_first_shrink
		ave_first_shrink = result[12]
		global ave_second_shrink
		ave_second_shrink = result[13]
		global ave_other_shrink
		ave_other_shrink = result[14]
		global times_fix_point
		times_fix_point = result[15]
		global ave_blocker_ignore
		ave_blocker_ignore = result[16]
	
	return st

def cpi2cnf_CompileAll(file_name):

	output_file_path = case_output_file_path + file_name + '/' + file_name + '.cnf'
	
	result = []
	result = cdnf.get_dual_rail(var_index_map)
	global var_index_dual_rail_map
	var_index_dual_rail_map = result[0]
	global index_var_dual_rail_map
	index_var_dual_rail_map = result[1]

	# print var_index_dual_rail_map
	# print index_var_dual_rail_map

	result = []
	result = cdnf.get_cdnf(file_name, cover_PI, index_var_dual_rail_map)
	global pi
	pi = result[0]
	global min
	min = result[1]
	global fact
	fact = result[2]
	global dr
	dr = result[3]

	cdnf.output_cnf(output_file_path, var_index_dual_rail_map, pi, min, dr, fact)

def cdnf2out_CompileAll(file_name):

	input_file_path = case_input_file_path + file_name + '/' + file_name + '.cnf'
	output_file_path = case_output_file_path + file_name + '/' + file_name + '.out'

	st = compile_prime.compile_all_NPCNF(CompileAll_file_path, LIMIT_TIME, str(OUTPUT_MOD), input_file_path, output_file_path, IS_COMPUTE_PIN, str(BACKTRACK_MOD_CA))

	global is_memory_out_all
	is_memory_out_all = compile_prime.decode(output_file_path, IS_COMPUTE_PIN, OUTPUT_MOD)

	result= []
	result = compile_prime.read_all_PI(output_file_path, OUTPUT_MOD)
	# global all_PI
	# all_PI = result[0]
	global num_all_PI
	num_all_PI = result[0]
	global CompileAll_memory
	CompileAll_memory = result[1]
	global CompileAll_time
	CompileAll_time = result[2]
	
	return st

def output(file_name):
	# file_path = case_output_file_path + file_name + '/' + file_name + '.res'
	# output the result to the new file 
	file_path = result_output_file_path + file_name + '.res'
	f = file(file_path, 'w+')

	if is_time_out_all:
		global is_memory_out_all
		is_memory_out_all = False
	if is_time_out_cover:
		global is_memory_out_cover
		is_memory_out_cover = False

	if is_memory_out_all or is_memory_out_cover:
		mem_info = 'Total memory usage (kb)\t\t: ' + str(LIMIT_MEMORY) + '\n'
	else:
		mem_info = 'Total memory usage (kb)\t\t: ' + str(max(CompileCover_memory, CompileAll_memory)) + '\n'
	f.writelines(mem_info)

	if is_time_out_all or is_time_out_cover:
		time_info = 'Total time usage (s)\t\t: ' + str(LIMIT_TIME) + '\n'
	else:
		time_info = 'Total time usage (s)\t\t: ' + str(CompileCover_time + CompileAll_time) + '\n'
	f.writelines(time_info)

	if IS_COMPUTE_PIN:
		PIn_size_info = 'The number of prime implicants\t: ' + str(num_all_PI) + '\n'
		f.writelines(PIn_size_info)
		PIe_size_info = 'The number of prime implicates\t: ' + str(num_API) + '\n'
		f.writelines(PIe_size_info)
	else:
		PIn_size_info = 'The number of prime implicates\t: ' + str(num_all_PI) + '\n'
		f.writelines(PIn_size_info)
		PIe_size_info = 'The number of prime implicants\t: ' + str(num_API) + '\n'
		f.writelines(PIe_size_info)

	date_info = 'The number of API\t\t: ' + str(num_API) + '\n'
	f.writelines(date_info)
	date_info = 'The times of call SAT\t\t: ' + str(times_SAT) + '\n'
	f.writelines(date_info)
	date_info = 'The average size of API\t\t: ' + str(ave_size_API) + '\n'
	f.writelines(date_info)
	
	f.close()

def output_cover_analysis(file_name):
	size_analysis = {}
	output = []
	# output_file_path_res = case_output_file_path + file_name + '/' + file_name + '.res'
	output_file_path_res = result_output_file_path + file_name + '.res'

	max_size = 0

	f = open(output_file_path_res, 'r')
	for line in f:
		output.append(line)
	f.close()

	for item in cover_PI:
		size = len(item)
		if size > max_size:
			max_size = size
		if size in size_analysis:
			size_analysis[size] = size_analysis[size] + 1
		else:
			size_analysis[size]	= 1

	f = file(output_file_path_res, 'w+')
	f.writelines(output)
	for item in range(max_size + 1):
		if item in size_analysis:
			size = str(item)
			num = str(size_analysis[item])
			f.writelines(size + ':' + num + '\n')
	
	f.close()

def CoAPI(file_name):

	if IS_COHERENT_OPEN:
		is_coherent = False
	else:
		is_coherent = False
	
	clear()
	get_info(file_name)
	st = pncnf2cpi(file_name, is_coherent)
	if st == 2:
		cpi2cnf_CompileAll(file_name)
		st = cdnf2out_CompileAll(file_name)
		if st:
			if is_memory_out_all:
				print 'CompileAll memory out!'
		else:
			global is_time_out_all
			is_time_out_all = True
			print 'CompileAll time out!'
	elif st == 1:
		global is_time_out_cover
		is_time_out_cover = True
		print 'CompileCover time out!'
	else:
		global is_memory_out_cover
		is_memory_out_cover = True
		print 'CompileCover memory out!'

	output(file_name)
	output_cover_analysis(file_name)

def CoAPIs():
	input_file_path = WORKSPACE + 'example/' + BENCHMARK
	pathDir = os.listdir(input_file_path)
	file_names = []
	for allDir in pathDir:
 		file_name = allDir
 		pattern = '\-n|\-p'
 		regex = re.compile(pattern, flags = re.IGNORECASE)
  		file_names.append(regex.split(file_name)[0])

  	file_names = set(file_names)
  		# break
  	# print file_names
	i = 0
	for file_name in file_names:
		i = i + 1
		print i,'th ' + file_name+' solving...' + '['+time.strftime('%Y-%m-%d %H:%M:%S')+']'
		CoAPI(file_name)
		print 'CompileCover time:', CompileCover_time, 'CompileAll time:', CompileAll_time, '#Primes: ', num_all_PI
		clean(file_name)
		print file_name+' solved' + '['+time.strftime('%Y-%m-%d %H:%M:%S')+']'

def parser_CoAPI():

	parser = argparse.ArgumentParser()
	parser.add_argument("-cc", type = str, default = 'CompileCover_fi_it_fb', help = "CompileCover core")
	parser.add_argument("-ac", type = str, default = 'CompileAll', help = "CompileAll core")
	parser.add_argument("-op", type = int, choices = [1, 2], default = 2, help = "is output mod (1: output #primes; 2: output all primes)")
	parser.add_argument("-bm", type = str, default = 'test', help = "benchmark")
	parser.add_argument("-lt", type = int, default = 3600 * 1, help = "limit time")
	parser.add_argument("-pin", type = int, choices = [0, 1], default = 0, help = "is the computation of prime implicant (0: False; 1: True)")
	parser.add_argument("-co", type = int, choices = [0, 1], default = 0, help = "is open coherent (0: False; 1: True)")
	parser.add_argument("-uca", type = int, choices = [0, 1], default = 0, help = "is using UC to over-approximation (0: False; 1: True)")
	parser.add_argument("-qx", type = int, choices = [0, 1], default = 0, help = "is using QuickXplain (0: False; 1: True)")
	parser.add_argument("-zm", type = int, choices = [0, 1], default = 0, help = "is using the method proposed by Lintao Zhang and Sharad Malik in SAT'03 (0: False; 1: True)")
	parser.add_argument("-li", type = int, default = 0, help = "limit iterations")
	parser.add_argument("-btcc", type = int, choices = [0, 1], default = 0, help = "is backtrack mod for CompileCover (0: backtrack; 1: backjump)")
	parser.add_argument("-btca", type = int, choices = [0, 1], default = 1, help = "is backtrack mod for CompileAll (0: backtrack; 1: backjump)")

	args = parser.parse_args()

	global BENCHMARK
	BENCHMARK = args.bm + '/'
	global LIMIT_TIME
	LIMIT_TIME = args.lt
	global OUTPUT_MOD
	OUTPUT_MOD = args.op
	global IS_COMPUTE_PIN
	if args.pin == 0:
		IS_COMPUTE_PIN = False
	else:
		IS_COMPUTE_PIN = True
	global IS_COHERENT_OPEN
	if args.co == 0:
		IS_COHERENT_OPEN = False
	else:
		IS_COHERENT_OPEN = True
	global IS_UCA_OPEN
	if args.uca == 0:
		IS_UCA_OPEN = False
	else:
		IS_UCA_OPEN = True
	global IS_QX_OPEN
	if args.qx == 0:
		IS_QX_OPEN = False
	else:
		IS_QX_OPEN = True
	global IS_ZM_OPEN
	if args.zm == 0:
		IS_ZM_OPEN = False
	else:
		IS_ZM_OPEN = True
	global LIMIT_ITERATION
	LIMIT_ITERATION = args.li
	global BACKTRACK_MOD_CC
	BACKTRACK_MOD_CC = args.btcc
	global BACKTRACK_MOD_CA
	BACKTRACK_MOD_CA = args.btca

	global CompileCover_file_path
	CompileCover_file_path = CompileCover_file_path + args.cc
	global CompileAll_file_path
	CompileAll_file_path = CompileAll_file_path + args.ac
	global case_input_file_path
	case_input_file_path = case_input_file_path + BENCHMARK
	global case_output_file_path
	case_output_file_path = case_output_file_path + BENCHMARK
	global result_output_file_path
	result_output_file_path = result_output_file_path + BENCHMARK

	# new result path
	if not os.path.exists(result_output_file_path):
		os.mkdir(result_output_file_path)

def print_status():
	print 'CompileCover \t\t\t=', CompileCover_file_path
	print 'CompileAll \t\t\t\t=', CompileAll_file_path
	print 'BENCHMARK \t\t\t\t=', BENCHMARK
	print 'LIMIT_TIME \t\t\t\t=', LIMIT_TIME
	print 'IS_COMPUTE_PIN \t\t\t=', IS_COMPUTE_PIN

def check_parameter():
	if IS_QX_OPEN and IS_ZM_OPEN:
		print "The mode of shrinking UC (IS_QX_OPEN & IS_ZM_OPEN) is error!"
		return False
	elif IS_QX_OPEN and IS_UCA_OPEN:
		print "The mode of shrinking UC (IS_QX_OPEN & IS_UCA_OPEN) is error!"
		return False
	elif IS_ZM_OPEN and IS_UCA_OPEN:
		print "The mode of shrinking UC (IS_ZM_OPEN & IS_UCA_OPEN) is error!"
		return False
	elif (not IS_ZM_OPEN) and (not IS_UCA_OPEN) and (not IS_QX_OPEN):
		print "The mode of shrinking UC (!IS_ZM_OPEN & !IS_UCA_OPEN & !IS_QX_OPEN) is error!"
		return False

	if IS_QX_OPEN and LIMIT_ITERATION != 0:
		print "the mode of shrinking UC (IS_QX_OPEN & LIMIT_ITERATION) is error!"
		return False
	
	return True

if __name__ == "__main__":

	parser_CoAPI()
	print '******************** STATUS ********************'
	print_status()

	print '******************** SOLVE ********************'
	if check_parameter():
		CoAPIs()
	print '********************  END  ********************'
