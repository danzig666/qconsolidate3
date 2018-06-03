UI_PATH=ui
UI_SOURCES=$(wildcard $(UI_PATH)/*.ui)
UI_FILES=$(patsubst $(UI_PATH)/%.ui, $(UI_PATH)/ui_%.py, $(UI_SOURCES))

RES_PATH=.
RES_SOURCES=$(wildcard $(RES_PATH)/*.qrc)
RES_FILES=$(patsubst $(RES_PATH)/%.qrc, $(RES_PATH)/%_rc.py, $(RES_SOURCES))

PRO_PATH=.
PRO_FILES=$(wildcard $(PRO_PATH)/*.pro)

ALL_FILES= ${RES_FILES} ${UI_FILES} ${LANG_FILES}

all: $(ALL_FILES)

ui: $(UI_FILES)

ts: $(PRO_FILES)
	pylupdate4 -verbose $<

lang: $(LANG_FILES)

res: $(RES_FILES)

$(UI_FILES): $(UI_PATH)/ui_%.py: $(UI_PATH)/%.ui
	pyuic5 -d -o $@ $<

$(RES_FILES): $(RES_PATH)/%_rc.py: $(RES_PATH)/%.qrc
	pyrcc5 -o $@ $<

pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude resources_rc.py . || true

clean:
	rm -f $(ALL_FILES)
	find -name "*.pyc" -exec rm -f {} \;
	rm -f *.zip

package:
	cd .. && rm -f *.zip && zip -r qconsolidate.zip qconsolidate -x \*.pyc \*.ts \*.ui \*.qrc \*.pro \*~ \*.git\* \*Makefile*
	mv ../qconsolidate.zip .

upload:
	plugin_uploader.py qconsolidate.zip
