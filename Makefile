PREFIX = /usr/local/bin

SCRIPT_NAME = milk
SCRIPT = src/main.py

all: install

install:
	@echo "Installing $(SCRIPT_NAME) to $(PREFIX)..."
	@install -m 0755 $(SCRIPT) $(PREFIX)/$(SCRIPT_NAME)
	@echo "Installation complete."

uninstall:
	@echo "Uninstalling $(SCRIPT_NAME) from $(PREFIX)..."
	@rm -f $(PREFIX)/$(SCRIPT_NAME)
	@echo "Uninstallation complete."

clean:
	@echo "Nothing to clean."

.PHONY: all install uninstall clean