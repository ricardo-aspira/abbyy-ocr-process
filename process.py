#!/usr/bin/python

# Usage: process.py <input file> <output file> [-l <Language>] [-pdf|-txt|-rtf|-docx|-xml]

import argparse
import os
import time

from AbbyyOnlineSdk import *

processor = None

format_extension = {}
format_extension['docx'] = 'docx'
format_extension['pdfa'] = 'pdf'
format_extension['pdfTextAndImages'] = 'pdf'
format_extension['pdfSearchable'] = 'pdf'
format_extension['pptx'] = 'pptx'
format_extension['rtf'] = 'rtf'
format_extension['txt'] = 'txt'
format_extension['txtUnstructured'] = 'txt'
format_extension['xlsx'] = 'xlsx'
format_extension['xml'] = 'xml'
format_extension['xmlForCorrectedImage'] = 'xml'

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
def process_file(options, input_file_path, output_file_path):
		
	print("Uploading..")
	settings = ProcessingSettings()
	settings.Operation = options['operation']
	settings.Language = options['language']
	settings.OutputFormat = options['outputFormat']
	settings.TextType = options['textType']
	task = processor.process(input_file_path, settings)
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
			processor.download_result(task, output_file_path)
			print("Result was written to {}".format(output_file_path))
	else:
		print("Error processing task")


def create_parser():
	parser = argparse.ArgumentParser(description="Recognize a file via web service")

	parser.add_argument('-l', '--language', default='English', help='Recognition language (default: %(default)s)')

	group_operation = parser.add_mutually_exclusive_group()
	group_operation.add_argument('-image', action='store_const', const='processImage', dest='operation', default='processImage')
	group_operation.add_argument('-textField', action='store_const', const='processTextField', dest='operation')
	
	group_process_image_export_format = parser.add_mutually_exclusive_group()
	group_process_image_export_format.add_argument('-txt', action='store_const', const='txt', dest='format', default='txt')
	group_process_image_export_format.add_argument('-txtUnstructured', action='store_const', const='txtUnstructured', dest='format')
	group_process_image_export_format.add_argument('-rtf', action='store_const', const='rtf', dest='format')
	group_process_image_export_format.add_argument('-docx', action='store_const', const='docx', dest='format')
	group_process_image_export_format.add_argument('-xlsx', action='store_const', const='xlsx', dest='format')
	group_process_image_export_format.add_argument('-pptx', action='store_const', const='pptx', dest='format')
	group_process_image_export_format.add_argument('-pdfSearchable', action='store_const', const='pdfSearchable', dest='format')
	group_process_image_export_format.add_argument('-pdfa', action='store_const', const='pdfa', dest='format')
	group_process_image_export_format.add_argument('-pdfTextAndImages', action='store_const', const='pdfTextAndImages', dest='format')
	group_process_image_export_format.add_argument('-xml', action='store_const', const='xml', dest='format')
	group_process_image_export_format.add_argument('-xmlForCorrectedImage', action='store_const', const='xmlForCorrectedImage', dest='format')
	
	group_process_text_field_text_type = parser.add_mutually_exclusive_group()
	group_process_text_field_text_type.add_argument('-allTextTypes', action='store_const', const='allTextTypes', dest='textType', default='normal,typewriter,matrix,index,ocrA,ocrB,e13b,cmc7,gothic')
	group_process_text_field_text_type.add_argument('-normal', action='store_const', const='normal', dest='textType')
	group_process_text_field_text_type.add_argument('-typewriter', action='store_const', const='typewriter', dest='textType')
	group_process_text_field_text_type.add_argument('-matrix', action='store_const', const='matrix', dest='textType')
	group_process_text_field_text_type.add_argument('-index', action='store_const', const='index', dest='textType')
	group_process_text_field_text_type.add_argument('-ocrA', action='store_const', const='ocrA', dest='textType')
	group_process_text_field_text_type.add_argument('-ocrB', action='store_const', const='ocrB', dest='textType')
	group_process_text_field_text_type.add_argument('-e13b', action='store_const', const='e13b', dest='textType')
	group_process_text_field_text_type.add_argument('-cmc7', action='store_const', const='cmc7', dest='textType')
	group_process_text_field_text_type.add_argument('-gothic', action='store_const', const='gothic', dest='textType')

	return parser


def main():
	global processor
	processor = AbbyyOnlineSdk()

	setup_processor()

	args = create_parser().parse_args()

	options = {
		"language": args.language,
		"operation": args.operation,
		"outputFormat": args.format,
		"textType": args.textType
	}

	input_folder  = os.path.join(os.getcwd(), 'input')
	output_folder = os.path.join(os.getcwd(), 'output')
	extension = format_extension[options['outputFormat']]
	if options['operation'] == 'processTextField':
		extension = format_extension['xml']

	for root, dirs, files in os.walk(input_folder):
		for file in files:
			nome_arquivo_saida = os.path.splitext(file)[0]
			if nome_arquivo_saida.startswith('.'):
				continue

			caminho_arquivo_entrada = os.path.join(input_folder, file)
			caminho_arquivo_saida   = os.path.join(output_folder, \
										'.'.join((nome_arquivo_saida, extension)))

			if os.path.isfile(caminho_arquivo_entrada):
				process_file(options, caminho_arquivo_entrada, caminho_arquivo_saida)
			else:
				print("No such file: {}".format(caminho_arquivo_entrada))


if __name__ == "__main__":
	main()
