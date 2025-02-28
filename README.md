# GMFLF——General Model Fault Localization Framework

A general framework for applying SBFL techniques to fault localization of models is presented, including five modules: Generation of Model Spectrum, Construction of Candidate Formula Pools, Construction of an Optimal Subset of Formulas, Training of the Fault Localization Model, Production of Final Ranking Results. This repository is associated with the paper: **Automated Spectrum-based Model Fault Localization Within a General Search Framework**, to be published in *The Journal of Systems & Software*.

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
            - `randModel.py`  Randomly generated state machine models
        - `PathGeneration`
            - `run.py`  Main program (It would call functions in other programs)
        - `EFSMparser`   Model automatically generates files (This folder contains programs that are called by other programs)
        - `inputGenerationImprove`  Model automatically generates files (This folder contains programs that are called by other programs)
        - `pyauparser`  Model automatically generates files (This folder contains programs that are called by other programs)
    - **Injecting mutation operators into the models**
        - `Mutation`
            - `run.py`  Main program: generation of variant models
            - `operator_replace.py`   Set the operator variation
    - **Spectrum generation**
        - `spectrumGeneration`
            - `consistencyCheck.py`   Perform the variation model, recording the trajectory and success and failure information
            - `coverMatrix.py`   Generate a coverage matrix (spectra)

2. **efsm\WOA_modelSpectrum** —— Module: Construction of an Optimal Subset of Formulas
    - `dataProcessing_GP.py`   Calculating the suspiciousness value of the GP formula
    - `dataProcessing_Greatest.py`   Calculate the suspiciousness values
    - `dataProcessing_MULTRIC.py`   Calculate the suspiciousness values
    - `dataProcessing_PRINCE.py`   Calculate the suspiciousness values
    - `Kmeans.py`   Normalization of the training set and clustering
    - `chooseStatic.py`   Selecting a subset of formulas using the KWOA method

3. **LTR** —— Module: Training of the Fault Localization Model & Production of Final Ranking Results
    - `RankLib.py`   Generate RankLib toolkit specific format files, training files, test files, and command line commands
    - The training files and test files were generated using the RankLib toolkit.

4. **efsm\dataAnalysis**
    - **Analysis and evaluation**
        - `func.py`   general function
        - `maximalCombine.py`   To evaluate the effects of the 7 best SBFL formula combinations
        - `maximals_exam_statistics.py`
        - `gpCombine.py`   To compare the effects of Random-LTR, KWOA-LTR with individual formulas
        - `gp_exam_statistics.py`
        - `result`   evaluation Results (including EXAM score, Accuracy, wrong ranking, etc.)
        - The remaining files are faulty versions' ranking results after learning-to-rank training
