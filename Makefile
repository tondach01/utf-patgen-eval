.PHONY: clean all

clean:
	rm -rf logs/ data/hyphbench_full.wlh data/*.txt *.txt *.csv *.png pattmp.*

evaluation_results.csv:
	ITERATIONS=5 JOBS=32 DATA_DIR=../hyph-bench/data PROFILES_DIR=../hyph-bench/profiles ./evaluate.sh

conflicts.csv: data/hyphbench_full.in
	python combine_datasets.py -f data/hyphbench_full.in -o data

conflict_table.txt: conflicts.csv
	python csv2latex.py -f conflicts.csv -o conflict_table.txt

combined_dataset.csv: data/hyphbench_full.in
	python combine_datasets.py -f data/hyphbench_full.in -o data

combined_dataset_table.txt: combined_dataset.csv
	python csv2latex.py -f combined_dataset.csv -o combined_dataset_table.txt -l "tab:combined-dataset" -s "The combined dataset" -d "The combined dataset: the parameters of the merged collection"

time.csv: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

time.png: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

time_table.txt: time.csv
	python csv2latex.py -f time.csv -o time_table.txt

memory.csv: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

memory.png: evaluation_results.csv
	source .venv/bin/activate; python process_results.py

memory_table.txt: memory.csv
	python csv2latex.py -f memory.csv -o memory_table.txt

all: conflict_table.txt combined_dataset_table.txt time_table.txt memory_table.txt time.png memory.png
	rm conflicts.csv combined_dataset.csv time.csv memory.csv
