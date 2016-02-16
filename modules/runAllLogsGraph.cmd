@ECHO OFF

for %%f in (test_logs/*.csv) do (
	Python Tester.py -dir test_logs -l %%~nf.csv -g %%~nf > test_results/%%~nf.txt
)
