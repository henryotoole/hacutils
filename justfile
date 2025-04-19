project_name := "hacutils"
version := `./.venv/bin/python3 -c "import toml; print(toml.load('./pyproject.toml')['project']['version'])"`

# Assembles and produces the distributable code in the module release folder.
build:
	python -m build
	cp ./dist/{{project_name}}-{{version}}.tar.gz ./{{project_name}}/{{project_name}}-{{version}}.tar.gz