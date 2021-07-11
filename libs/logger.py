import logging

def logGenerator(m_log_file):
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	formatter=logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
	file_handler=logging.FileHandler(filename=m_log_file)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger