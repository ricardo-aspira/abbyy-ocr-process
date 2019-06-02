#!/usr/bin/python

# Usage: process.py <input file> <output file> [-l <Language>] [-pdf|-txt|-rtf|-docx|-xml]

import argparse
import os
import time

from AbbyyOnlineSdk import *

processor = None

def setup_processor():

	if "ABBYY_SERVER_URL" in os.environ:
		processor.ServerUrl = os.environ["ABBYY_SERVER_URL"]
		print("processor.ServerUrl=" + processor.ServerUrl)

	if "ABBYY_APPID" in os.environ:
		processor.ApplicationId = os.environ["ABBYY_APPID"]
		print("processor.ApplicationId=" + processor.ApplicationId)

	if "ABBYY_PWD" in os.environ:
		processor.Password = os.environ["ABBYY_PWD"]
		print("processor.Password=" + processor.Password)

	# Proxy settings
	if "http_proxy" in os.environ:
		proxy_string = os.environ["http_proxy"]
		print("Using http proxy at {}".format(proxy_string))
		processor.Proxies["http"] = proxy_string

	if "https_proxy" in os.environ:
		proxy_string = os.environ["https_proxy"]
		print("Using https proxy at {}".format(proxy_string))
		processor.Proxies["https"] = proxy_string


# Recognize a file at filePath and save result to resultFilePath
def recognize_file(file_path, result_file_path, language, input_dir, output_dir, output_format):
	
	file_path = os.path.join(input_dir, file_path)
	result_file_path = os.path.join(output_dir, result_file_path)
	
	print("Uploading..")
	settings = ProcessingSettings()
	settings.Language = language
	settings.OutputFormat = output_format
	task = processor.process_image(file_path, settings)
	if task is None:
		print("Error")
		return
	if task.Status == "NotEnoughCredits":
		print("Not enough credits to process the document. Please add more pages to your application's account.")
		return

	print("Id = {}".format(task.Id))
	print("Status = {}".format(task.Status))

	# Wait for the task to be completed
	print("Waiting..")
	# Note: it's recommended that your application waits at least 2 seconds
	# before making the first getTaskStatus request and also between such requests
	# for the same task. Making requests more often will not improve your
	# application performance.
	# Note: if your application queues several files and waits for them
	# it's recommended that you use listFinishedTasks instead (which is described
	# at https://ocrsdk.com/documentation/apireference/listFinishedTasks/).

	while task.is_active():
		time.sleep(5)
		print(".")
		task = processor.get_task_status(task)

	print("Status = {}".format(task.Status))

	if task.Status == "Completed":
		if task.DownloadUrl is not None:
			processor.download_result(task, result_file_path)
			print("Result was written to {}".format(result_file_path))
	else:
		print("Error processing task")


def create_parser():
	parser = argparse.ArgumentParser(description="Recognize a file via web service")
	parser.add_argument('source_file')
	parser.add_argument('target_file')

	parser.add_argument('-l', '--language', default='English', help='Recognition language (default: %(default)s)')
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-txt', action='store_const', const='txt', dest='format', default='txt')
	group.add_argument('-txtUnstructured', action='store_const', const='txtUnstructured', dest='format')
	group.add_argument('-rtf', action='store_const', const='rtf', dest='format')
	group.add_argument('-docx', action='store_const', const='docx', dest='format')
	group.add_argument('-xlsx', action='store_const', const='xlsx', dest='format')
	group.add_argument('-pptx', action='store_const', const='pptx', dest='format')
	group.add_argument('-pdfSearchable', action='store_const', const='pdfSearchable', dest='format')
	group.add_argument('-pdfa', action='store_const', const='pdfa', dest='format')
	group.add_argument('-pdfTextAndImages', action='store_const', const='pdfTextAndImages', dest='format')
	group.add_argument('-xml', action='store_const', const='xml', dest='format')
	group.add_argument('-xmlForCorrectedImage', action='store_const', const='xmlForCorrectedImage', dest='format')
	group.add_argument('-auto', action='store_const', const='auto', dest='format')

	return parser


def main():
	global processor
	processor = AbbyyOnlineSdk()

	setup_processor()

	args = create_parser().parse_args()

	source_file = args.source_file
	target_file = args.target_file
	language = args.language
	output_format = args.format

	input_dir  = './input'
	output_dir = './output'

	if '/' in source_file:
		raise Exception("The source_file should be a file name only and not a path. This file will be read from input folder inside the container that should be mapped to a folder of host.")

	if '/' in target_file:
		raise Exception("The target_file should be a file name only and not a path. This file will be saved into output folder inside the container that should be mapped to a folder of host.")

	if os.path.isfile(source_file):
		recognize_file(source_file, target_file, language, \
					input_dir, output_dir, output_format)
	else:
		print("No such file: {}".format(source_file))


if __name__ == "__main__":
	main()
