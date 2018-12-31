
CACHE=./reportcache


REPORTS=memberlist.csv qbolist.csv

VE=./qbo-venv
VEACT=${VE}/bin/activate

virtualenv: ${VEACT}

${VEACT}:
	python3 -m virtualenv ${VE}
	( \
	source ${VEACT} ; \
	pip install --upgrade pip ; \
	pip install -r requirements.txt; \
	) 




${CACHE}/memberlist.csv:  ../memberlist.csv
	cp $< $@


${CACHE}/qbolist.csv:
	(\
	source 
	./listcustomers.py | sort -k1 -n > $@  \
	)


