
SHELL=/bin/bash

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






CACHE=./reportcache


REPORTS=memberlist.csv qbolist.csv

REPORTFILES=$(addprefix ${CACHE}/,${REPORTS})

reports: ${REPORTFILES}

cleanreports:
	rm ${REPORTFILES}


${CACHE}/memberlist.csv:  ../memberlist.csv
	cp $< $@

${CACHE}/qbolist.csv:
	(\
	source ${VEACT} ;\
	./listcustomers.py | sort -k1 -n > $@  \
	)



