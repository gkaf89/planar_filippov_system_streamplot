TARGETS=Streamplots

TARGET_PDFS=$(patsubst %, %.pdf, $(TARGETS))

ARGS=$$pdflatex='pdflatex -synctex=1 -shell-escape'
PREVIEW=$$pdf_previewer='start evince'

.PHONY: all
all: $(TARGETS)

.PHONY: $(TARGETS)
$(TARGETS): % : %.pdf

%.pdf : %.tex
	latexmk -e $(ARGS) -pdf $^

.PHONY: clean
clean:
	echo "Removing files:" && find . -maxdepth 1 -type f | grep -vE '(\.(tex|bib|sty|sh|ps1|gitignore|otf|git)|^\./Makefile$$)' | xargs -I % sh -c '{ echo "%"; rm "%"; }'

