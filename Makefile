# Файл для установки, компиляции и т.д. скрипта

SCRIPT = proxies-taster
DESTDIR = /opt/proxies-taster
LIBDIR = ${DESTDIR}

LINKPATH = /usr/local/bin/${SCRIPT}

install:
	sudo chmod ugo+x proxies-taster; \
	pip install proxies-taster logging colorama --break-system-packages; \

	if [ ! -d "${LIBDIR}" ]; then \
	    sudo mkdir -p "${LIBDIR}"; \
	fi; \
	sudo cp proxies_parser_logger.py "${LIBDIR}/proxies_parser_logger.py"; \
	sudo cp proxies-taster "${DESTDIR}/${SCRIPT}"; \

	sudo ln -s "${DESTDIR}/${SCRIPT}" "${LINKPATH}"
install-dev:
	sudo chmod ugo+x proxies-taster; \
	pip install -r requirements.txt --break-system-packages \

	if [ ! -d "${LIBDIR}" ]; then \
	    sudo mkdir -p "${LIBDIR}"; \
	fi; \
	sudo cp proxies_parser_logger.py "${LIBDIR/proxies_parser_logger.py}"; \
	sudo cp proxies-taster "${DESTDIR}/${SCRIPT}"; \

	sudo ln -s "${DESTDIR}/${SCRIPT}" "${LINKPATH}"
uninstall:
	sudo rm "${LINKPATH}"
	sudo rm "${DESTDIR}/${SCRIPT}"; \
	sudo rm "${LIBDIR}/proxies_parser_logger.py"
update:
	make uninstall && make install
update-dev: 
	make uninstall && make install-dev
