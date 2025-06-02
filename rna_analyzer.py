# -*- coding: utf-8 -*-
"""
Created on Mon May 26 09:00:18 2025

@author: enich
"""

import matplotlib.pyplot as plt
import seaborn as sns
from cmapPy.pandasGEXpress import parse
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from gseapy import gsva

gct_data = parse.parse("PAAD.gct")
expression_data = gct_data.data_df
metadata = gct_data.col_metadata_df
cleaned_data = expression_data.dropna()

plt.figure(figsize=(14, 6))
sns.boxplot(data=cleaned_data.T)
plt.xticks([], [])
plt.xlabel("Samples")
plt.ylabel("Gene Expression")
plt.title("Boxplot of Gene Expression for All Samples")
plt.tight_layout()
plt.show()

X = StandardScaler().fit_transform(cleaned_data.T)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)
metadata = gct_data.col_metadata_df
histology = metadata["histological_type_other"].values

plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=histology, palette="Set2")
plt.title("PCA of Samples (covered by Histology)")
plt.xlabel("PCA1")
plt.ylabel("PCA2")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

exocrine_samples = metadata[metadata["histological_type_other"] != "Neuroendocrine"].index
exocrine_expression = cleaned_data[exocrine_samples]


with open("type1_IFN.txt", "r") as f:
    ifn_genes = [line.strip() for line in f]

expression_gsva = exocrine_expression.copy()
expression_gsva = expression_gsva.loc[expression_gsva.index.intersection(ifn_genes)]

exocrine_expression.index = exocrine_expression.index.str.upper()
ifn_genes = [g.strip().upper() for g in ifn_genes]
matching_genes = [gene for gene in ifn_genes if gene in exocrine_expression.index]

with open("ifn_signature.gmt", "w") as f:
    f.write("IFN_Signature\tNA\t" + "\t".join(matching_genes) + "\n")

filtered_expression = exocrine_expression.loc[matching_genes].astype(float)
gsva_results = gsva(data=exocrine_expression, gene_sets="ifn_signature.gmt",
                    method="gsva", outdir=None, verbose=True, min_size=5)
gsva_results_df = gsva_results.res2d

plt.figure(figsize=(8, 5))
sns.histplot(gsva_results_df, kde=True, bins=30)
plt.title("Distribution of IFN Signature GSVA Scores")
plt.xlabel("GSVA Score")
plt.ylabel("Sample Count")
plt.tight_layout()
plt.show()