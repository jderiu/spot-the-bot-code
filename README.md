# Spot The Bot: A Robust and Efficient Framework for the Evaluation of Conversational Dialogue Systems

## General Installation
You need to install a  [MongoDB](https://www.mongodb.com/try/download/community) v4.2.9 Server somewhere. All the conversation data is stored there.
Unzip `data_dump/MongoDump.zip` and then import the files into your MongoDB (repeat this process for all 9 files):

```bash
mongoimport --db auto_judge_final --collection annotated-dialogues-full-convai2 --file annotated-dialogues-full-convai2.json --jsonArray --username <user_name>  --password <pw>
```

You need to install R...

You need to install Python 3.7, we suggest that you use [Anaconda](https://www.anaconda.com/products/individual):

```bash
$ conda env create -f environment.yml
```

Adapt the `config/annotation_app.json ` file as follows:
```json
{
    "host": "ip_address of your MongoDB Server",
    "port": "port of mongodb",
    "user": "mongodb user name",
    "password": "pw of mognodb user",
    "database_name": "auto_judge_final",
    "package_collection_name": "packed-dialogues-full-{domain_name}",
    "sampled_collection_name": "sampled-dialogues-full-{domain_name}",
    "labelled_collection_name": "annotated-dialogues-full-{domain_name}",
    "local_port": 5003,
    "max_package_per_user": 3
}
```

## Run the Annotation Tool
After you cloned the repository `cd/autojudge_annotaiton`:

To get the Rankings based on Bootstrap Sampling (Table 1):
 ```bash
$ python templates\src\segment_analysis\segmented_bootstrap_sampling.py
```

To get the pairwise win rates (Table 1):
 ```bash
$ python templates\src\segment_analysis\win_function.py
```
To perform the stability experiment (Figure 3a):
 ```bash
$ python templates\src\segment_analysis\ranking_significance.py
```

To perform the leave-one-out experiment (Figure 3b):
 ```bash
$ python templates\src\segment_analysis\ranking_significance.py -lo 1
```

## Ranking

## Survival Analysis

The survival analysis is implemented in R and uses the following packages:
* [survival](https://cran.r-project.org/web/packages/survival/index.html)
* [survminer](https://cran.r-project.org/web/packages/survminer/index.html) (needs a fortran compiler to install)
* [glrt](https://rdrr.io/cran/glrt/man/glrt-package.html)
* [icenReg](https://cran.r-project.org/web/packages/icenReg/index.html)

To export the survival data from your annotations run `python -m analysis.extract_event_data`.
This will create a csv file `event_data.csv` which is read by the R script.

Finally, run the R script at `analysis/survival.R`.

## IAA

## References
If you use this code, please cite us:

```
@inproceedings{deriu2020spot_the_bot,
  title = {{Spot The Bot: A Robust and Efficient Framework for the Evaluation of Conversational Dialogue Systems}},
  author = {Deriu, Jan and Tuggener, Don and von D{\"a}niken, Pius and Campos, Jon Ander and Rodrigo, Alvaro and, Belkacem, Thiziri and Soroa, Aitor and Agirre, Eneko and Cieliebak, Mark},
  booktitle = {Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing},
  address = {Online},
  year = {2020},
}
