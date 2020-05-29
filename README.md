# NLU Information Retreival modules
Multiple IR modules.

## 1. Requirements
### Install some python packages
In the project file, run:
```bash
pip install -r requirements.txt
```

### Install Java
Please follow https://docs.datastax.com/en/jdk-install/doc/jdk-install/installOpenJdkDeb.html to 
install open-jdk-8

### Install Pyluene
1. Please follow https://lucene.apache.org/pylucene/install.html to install pylucene.  
2. Note that when editing the Makefile, please follow https://blog.csdn.net/DSbatigol/article/details/14448151 for adding the Chinese analyzer.  
In the Makfile:
- Uncomment `#JARS+=$(SMARTCN_JAR)            # smart chinese analyzer` 
- add the line `--exclude org.apache.lucene.analysis.cn.smart.AnalyzerProfile` near `--exclude org.apache.lucene.sandbox.queries.regex.JakartaRegexpCapabilities`

## 2. ReadME Links:
- [Lucene searchers](nlu_IR/lucene_search) (including CosQA, SSQA, HotpotQA)