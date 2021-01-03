local_es:
	@echo "Launching Elasticsearch..."
	@elasticsearch -d

local_run:
	./launch_lcoal.sh

unittests:
	@echo "Unittesting Life_Web_Service..."
	@nosetests --all-modules --verbose --exe test