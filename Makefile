local_es:
	@echo "Launching Elasticsearch..."
	@elasticsearch -d

unittests:
	@echo "Unittesting Life_Web_Service..."
	@nosetests --all-modules --verbose --exe test