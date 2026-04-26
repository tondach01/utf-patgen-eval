.PHONY: clean

clean:
	rm -rf logs/ evaluation_results.csv hyphbench_full.wlh data/*.txt data/*.csv

evaluation_results.csv:
	ITERATIONS=5 JOBS=32 DATA_DIR=../hyph-bench/data PROFILES_DIR=../hyph-bench/profiles ./evaluate.sh

conflicts.csv: data/hyphbench_full.in
	python combine_datasets.py -f data/hyphbench_full.in -o data

conflict_table.txt: conflicts.csv
	python csv2latex.py -f conflicts.csv -o conflict_table.txt
