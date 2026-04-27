.PHONY: clean

clean:
	rm -rf logs/ data/hyphbench_full.wlh *.txt *.csv pattmp.*

evaluation_results.csv:
	module add texlive
	ITERATIONS=5 JOBS=32 DATA_DIR=../hyph-bench/data PROFILES_DIR=../hyph-bench/profiles ./evaluate.sh

conflicts.csv: data/hyphbench_full.in
	python combine_datasets.py -f data/hyphbench_full.in -o data

conflict_table.txt: conflicts.csv
	python csv2latex.py -f conflicts.csv -o conflict_table.txt

correctness.csv: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

correctness_table.txt: correctness.csv
	python csv2latex.py -f correctness.csv -o correctness_table.txt

time.csv: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

time_table.txt: time.csv
	python csv2latex.py -f time.csv -o time_table.txt

memory.csv: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

memory_table.txt: memory.csv
	python csv2latex.py -f memory.csv -o memory_table.txt
