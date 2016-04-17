# QCAPI
(unofficial) Python library and CLI tools for working with the QuantConnect API

## QCProject

List projects in your account: `$ ./qcproject ls --username $USERNAME --password $PASSWORD`

Create a new project: `$ ./qcproject init --name MyProject --username $USERNAME --password $PASSWORD`

Connect to an existing project: `$ ./qcproject init --project_id=44343 --username $USERNAME --password $PASSWORD`

Delete a project: `$ ./qcproject delete --project_id=3434343`

## QCSync

You must first initialize a project in the current directory with `qcproject`.

Pull remote code to CWD: `./qcsync pull`

Push local code to QC: `./qcsync push`

See differences between local and remote code that would be overritten by a push/pull: `./qcsync diff`

## QCBacktest

Compile your project: `./qcbacktest build`

Run a backtest on your project: `./qcbacktest backtest --name=MyBacktest`

using a previous compile: `./qcbacktest --compile_id=3434234j3fdf`

Delete a backtest: `./qcbacktest delete --backtest_id=34234jdfdf`

## QCAPI

You can automate your own workflows using the classes in `qcapi.py`.
