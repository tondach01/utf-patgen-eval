.PHONY: clean

clean:
	rm -rf logs/ evaluation_results.csv

evaluation_results.csv:
	ITERATIONS=5 DATA_DIR=../hyph-bench/data PROFILES_DIR=../hyph-bench/profiles ./evaluate.sh