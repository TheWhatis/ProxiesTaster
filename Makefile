# Файл для установки, компиляции и т.д. скрипта

LIBDIR = /usr/lib
SCRIPT = proxies-taster
DISTDIR = /usr/bin

install:
	pip install proxies-taster logging colorama

	if [ ! -d "${LIBDIR}" ]; then
		sudo mkdir -p "${LIBDIR}"
	fi
	sudo cp proxies_parser_logger.py "${LIBDIR/proxies_parser_logger.py}"
	sudo cp proxies-taster "${DIST}/${SCRIPT}"
install-dev:
	pip install -r requirements.txt

	if [ ! -d "${LIBDIR}" ]; then
		sudo mkdir -p "${LIBDIR}"
	fi
	sudo cp proxies_parser_logger.py "${LIBDIR/proxies_parser_logger.py}"
	sudo cp proxies-taster "${DIST}/${SCRIPT}"
uninstall:
	sudo rm "${DIST}/${SCRIPT}"
	sudo rm "${LIBDIR/proxies_parser_logger.py}"

	pip uninstall proxies-taster -y
	if [ -z $(pip show logging | grep ^Required-by | sed 's/Required-by://') ]; then
		pip uninstall logging -y
	fi

	if [ -z $(pip show colorama | grep ^Required-by | sed 's/Required-by://') ]; then
		pip uninstall colorama -y
	fi
