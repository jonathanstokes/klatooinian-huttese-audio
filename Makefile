.PHONY: init test run repl sample clean

init:
	poetry install

test:
	poetry run pytest -v

run:
	poetry run huttese "Bring me the plans, quickly!" --play

repl:
	poetry run huttese-repl

sample:
	@while read line; do \
	  echo ">> $$line"; \
	  poetry run huttese "$$line" --play; \
	done < samples/lines.txt

clean:
	rm -rf out/
	rm -f /tmp/huttese_*.wav

