#mcandrew

#--Set up environment variables
PYTHON ?= python3 -W ignore
R ?= Rscript

#--Set up virtual environment
VENV_DIR := .forecast
VENV_PYTHON := $(VENV_DIR)/bin/python -W ignore

full_analysis_pipeline: build_env data_pipeline quick_look_at_some_data

#--Build environment----------------------------------------------------------------------------
build_env:
	@echo "build forecast environment"
	@$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PYTHON) -m pip install -r requirements.txt

#--Download data--------------------------------------------------------------------------------
data_pipeline: download_ili download_target_data build_WHO_signal_season
download_ili:
	@echo "Downloading recent ILINet data"
	@$(VENV_PYTHON) ./analysis_data/build_ili_data.py
	@$(VENV_PYTHON) ./analysis_data/format_ili_data.py

download_target_data:
	@echo "Download target data"
	@$(R) ./data/target-data/get_target_data.R

build_WHO_signal_season:
	@echo "Downaload and format WHO data"
	@$(VENV_PYTHON) ./data/download_FluID_dataset.py
	@$(VENV_PYTHON) ./analysis_data/create_WWHO_ILI_Signal.py

quick_look_at_some_data:
	@echo "Quick look at some data"
	@$(VENV_PYTHON) ./analysis/predict_total_US_hosps_setup.py
