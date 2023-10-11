# Файл для установки, компиляции и т.д. скрипта

SCRIPT = proxies-taster
DESTDIR = /opt/proxies-taster
LIBDIR = ${DESTDIR}

LINKPATH = /usr/local/bin/${SCRIPT}

install:
	@if [ -f "${LINKPATH}" ]; then \
	    echo 'ProxiesTaster already installed'; \
	else \
	    if ! [ `stat -c %a "${SCRIPT}"` -eq 755 ]; then \
		sudo chmod ugo+x "${SCRIPT}"; \
	    else \
		echo "${SCRIPT} script already has all execute permission"; \
	    fi; \
	    pip install proxies-taster logging colorama --break-system-packages; \
	    if [ ! -d "${LIBDIR}" ]; then \
		sudo mkdir -p "${LIBDIR}"; \
	    fi; \
	    sudo cp proxies_parser_logger.py "${LIBDIR}/proxies_parser_logger.py"; \
	    sudo cp proxies-taster "${DESTDIR}/${SCRIPT}"; \
	    sudo ln -s "${DESTDIR}/${SCRIPT}" "${LINKPATH}"; \
	fi;
install-dev:
	@python -m venv .; \
	source bin/activate; \
	pip install -r requirements.txt --break-system-packages; \

	@if ! [ `stat -c %a "${SCRIPT}"` -eq 755 ]; then \
	    sudo chmod ugo+x "${SCRIPT}"; \
	else \
	    echo "${SCRIPT} script already has all execute permission"; \
	fi;
uninstall:
	@if [ ! -f "${LINKPATH}" ]; then \
	    echo 'ProxiesTaster already dont installed'; \
	else \
	    pip uninstall proxies-taster -y --break-system-packages; \
	    sudo rm -f "${LINKPATH}"; \
	    sudo rm -f "${DESTDIR}/${SCRIPT}"; \
	    sudo rm -f "${LIBDIR}/proxies_parser_logger.py"; \
	fi;
update:
	make uninstall && make install
update-dev:
	make uninstall && make install-dev
build:
	make install-dev; \

	@python setup.py sdist; \
	make clean -C docs/ && make markdown -C docs/ && make html -C docs/
