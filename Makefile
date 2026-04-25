.PHONY: clean

clean:
	rm -rf logs/ evaluation_results.csv hyphbench_full.wlh data/*.txt

evaluation_results.csv:
	ITERATIONS=5 DATA_DIR=../hyph-bench/data PROFILES_DIR=../hyph-bench/profiles ./evaluate.sh

hyphbench_full.wlh: data/hyphbench_full.in
	python combine_datasets.py -f data/hyphbench_full.in -o data
