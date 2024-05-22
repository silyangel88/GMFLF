# GMFLF——General Model Fault Localization Framework

A general framework for applying SBFL techniques to fault localization of models is presented, including five modules: Generation of Model Spectrum, Construction of Candidate Formula Pools, Construction of an Optimal Subset of Formulas, Training of the Fault Localization Model, Production of Final Ranking Results.

The following is the experimental code that implements this framework on Python 3.6 and Python 2, and version 2.1 of the RankLib toolkit (https://github.com/jattenberg/RankLib).

## Python 2 (setting: `requirements_python2.txt`)

1. **pyevolve** —— Module: Construction of Candidate Formula Pools
    - `pev_model.py`   Genetic Programming generates formulas to construct candidate formula pools
    - `spectrum`   Generated model spectrums
    - `GP_model`   Results of the GP formulas generated for each model

## Python 3.6 (setting: `requirements_python3.6.txt`)

1. **efsm** —— Module: Generation of Model Spectrum
    - **Test case generation**
        - `Specification`   The EFSM model protocol json files
        - `PathGeneration`
        - `run.py`   main program
        - `efsm_venv`  Model automatically generates files 
        - `EFSMparser`   Model automatically generates files
        - `inputGenerationImprove`  Model automatically generates files
        - `pyauparser`  Model automatically generates files
    - **Injecting mutation operators into the models**
        - `Mutation\run.py`  Generation of variant models
        - `Mutation\operator_replace.py`   Set the operator variation
    - **Spectrum generation**
        - `spectrumGeneration\consistencyCheck.py`   Perform the variation model, recording the trajectory and success and failure information
        - `spectrumGeneration\coverMatrix.py`   Generate a coverage matrix (spectrum)

2. **WOA_modelSpectrum** —— Module: Construction of an Optimal Subset of Formulas
    - `dataProcessing_GP.py`   Calculating the suspiciousness value of the GP formula
    - `dataProcessing_Maximal.py`   Calculate the suspiciousness values for the 7 optimal formulas
    - `Kmeans.py`   Normalization of the training set and clustering
    - `chooseStatic.py` & `KWOA.py`   Selecting a subset of formulas using the KWOA method

3. **LTR** —— Module: Training of the Fault Localization Model & Production of Final Ranking Results
    - `RankLib.py`   Generate RankLib toolkit specific format files, training files, test files, and command line commands
    - The training files and test files were generated using the RankLib toolkit.

4. **efsm\dataAnalysis**
    - **Analysis and evaluation**
        - `func.py`   general function
        - `singleSBFL.py`   To evaluate the effects of 16 individual classical SBFL formulas
        - `maximalCombine.py`   To evaluate the effects of the 7 best SBFL formula combinations
        - `comparisonKWOA.py`   To compare the effects of Random-LTR, KWOA-LTR with individual formulas
        - `result`   evaluation Results (including EXAM score, Accuracy, wrong ranking, etc.)
        - The remaining files are error ranking result files after learning-to-rank training
