DESTDIR = /
PREFIX := $(DESTDIR)usr
DATADIR := $(PREFIX)/share
MANDIR := $(DATADIR)/man
APPDIR := $(DATADIR)/applications
LICENSEDIR := $(DATADIR)/licenses

ICONSIZES := 16 32 64 128 256 512

default:
	@printf "There is nothing to do.\n"
	@printf "Run 'sudo make install' to install vimiv.\n"
	@printf "Run 'make options' for a list of all options.\n"

options: help
	@printf "\nOptions:\n"
	@printf "DESTDIR = $(DESTDIR)\n"
	@printf "PREFIX = $(PREFIX)\n"
	@printf "DATADIR = $(DATADIR)\n"
	@printf "MANDIR = $(MANDIR)\n"
	@printf "LICENSEDIR = $(LICENSEDIR)\n"

help:
	@printf "make help:              Print help.\n"
	@printf "make options:        	Print help and list all options.\n"
	@printf "make install:        	Install vimiv.\n"
	@printf "make uninstall: 	Uninstall vimiv.\n"
	@printf "make clean: 	        Remove build directories.\n"

install:
	python3 setup.py install --root=$(DESTDIR) --record=install_log.txt
	install -Dm644 misc/vimiv.desktop $(APPDIR)/vimiv.desktop
	install -Dm644 LICENSE $(LICENSEDIR)/vimiv/LICENSE
	install -Dm644 misc/vimiv.1 $(MANDIR)/man1/vimiv.1
	gzip -n -9 -f  $(MANDIR)/man1/vimiv.1
	$(foreach i,$(ICONSIZES),install -Dm644 icons/vimiv_${i}x${i}.png $(DATADIR)/icons/hicolor/${i}x${i}/apps/vimiv.png;)
	install -Dm644 icons/vimiv.svg $(DATADIR)/icons/hicolor/scalable/apps/vimiv.svg

uninstall:
	scripts/uninstall_pythonpkg.sh
	rm $(APPDIR)/vimiv.desktop
	rm -r $(LICENSEDIR)/vimiv
	rm $(MANDIR)/man1/vimiv.1.gz
	$(foreach i,$(ICONSIZES),rm $(DATADIR)/icons/hicolor/${i}x${i}/apps/vimiv.png;)
	rm $(DATADIR)/icons/hicolor/scalable/apps/vimiv.svg

clean:
	rm -rf build vimiv.egg-info/
