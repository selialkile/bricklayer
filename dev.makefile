bin_pip         = pip
bin_python      = python
venv_dir        = .venv
venv_bin        = $(venv_dir)/bin

bricklayer_cfg  = etc/bricklayer/bricklayer.ini.dev
bricklayer_env  = BRICKLAYERCONFIG=$(bricklayer_cfg)

clean:
	@find . -name '*.pyc' -delete

install_venv:
	$(bin_pip) install virtualenv

create_venv: install_venv
	virtualenv $(venv_dir)

bootstrap: create_venv
	$(venv_bin)/$(bin_pip) install -r pip-requires

test:
	@$(bricklayer_env) $(venv_bin)/nosetests $(TEST)
