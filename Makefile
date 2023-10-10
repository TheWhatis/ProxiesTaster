# Файл для установки, компиляции и т.д. скрипта

SCRIPT = proxies-taster
DISTDIR = /usr/bin

install:
	pip install proxies-taster logging colorama -y
	sudo cp proxies-taster "${DIST}/${SCRIPT}"
install-dev:
	pip install -r requirements.txt
	sudo cp proxies-taster "${DIST}/${SCRIPT}"
uninstall:
	sudo rm "${DIST}/${SCRIPT}"

	pip uninstall proxies-taster -y
	if [ -z $(pip show logging | grep ^Required-by | sed 's/Required-by://') ]; then
		pip uninstall logging -y
	fi

	if [ -z $(pip show colorama | grep ^Required-by | sed 's/Required-by://') ]; then
		pip uninstall colorama -y
	fi
