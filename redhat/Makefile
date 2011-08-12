# Makefile para pacotes Locaweb
#
SPECFILE := $(shell ls *.spec)
PACOTE := $(shell awk '/^Name:/ { print $$2 }' ${SPECFILE})
VERSAO := $(shell awk '/^Version:/ { print $$2 }' ${SPECFILE})
RELEASE := $(shell awk '/^Release:/ { print $$2 }' ${SPECFILE})
build_area := ${PWD}/build/rpm

all: clean
	mkdir -p build/${PACOTE}-${VERSAO}
	mkdir -p build/rpm/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	cp -a ../{bricklayer,deps.txt,doc,etc,MANIFEST.in,pkg_template,README.textile,setup.py,test,web,redhat/init.d} build/${PACOTE}-${VERSAO}/
	tar -czvpf ${build_area}/SOURCES/${PACOTE}-${VERSAO}.tar.gz -C build --exclude=test ${PACOTE}-${VERSAO}
	rm -rf build/${PACOTE}-${VERSAO}
	rpmbuild -ba --define "_topdir ${build_area}" --clean ${SPECFILE}
	mv ${build_area}/RPMS/*/${PACOTE}-${VERSAO}-${RELEASE}.*.rpm .
	mv ${build_area}/SRPMS/${PACOTE}-${VERSAO}-${RELEASE}.*.rpm .

.PHONY: clean

clean:
	find . -name \*.py[co] -exec rm -f {} \; 
	rm -rf build *.rpm
