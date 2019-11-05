
SHELL=/bin/bash

VE=./qbo-venv
VEACT=${VE}/bin/activate

virtualenv: ${VEACT}

${VEACT}:
	python3 -m venv ${VE}
	( \
	source ${VEACT} ; \
	pip install --upgrade pip ; \
	pip install -r requirements.txt; \
	) 




grab:
	mv -f  /home/asr/Downloads/Definitive\ Membership\ List\ -\ MasterMemberList.csv ../memberlist.csv


CACHE=./reportcache


REPORTS=memberlist.csv qbolist.csv accountlist

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

${CACHE}/accountlist:
	(\
	source ${VEACT} ;\
	./listaccounts.py > $@  \
	)



