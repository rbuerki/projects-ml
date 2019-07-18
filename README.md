# ML practice projects

A repository containing some (interesting) machine learning projects done for practice and kept for reference.
Each project has it's own README providing more details.

### Overview:

- **assosiation_rules_mining:** A repository containing code for implemenation of association rules mining (ARM, also called frequent itemset mining) with the apriori algorithm. In this case we use it for Market Basket Analysis. There is an implementation from scratch and a real use case on a b2b retail dataset using the MLextnd package.

- **customer_lifetime_value_modelling:**  A project predicting (residual) customer lifetime value (clv) in non-contracutal business.
  Methodology is based on paper by Dr. Peter Fader of Wharton, the underlying math is handled by the `lifetimes` package. The project highlights some problems of this approach.

- **customer_segmentation_unsupervised_kmeans:** Finding customer segments with PCA and k-means. Note: Everything in this
  project has been applied on a much more complex dataset in the Starbucks' segmentation challenge project.
  _In the resources folder are several notebooks on different unsupervised algorithms from Udacity's MLE nanodegree course._

- **nlp_classification_webapp_disaster_response:** Pt. 1: NLP Classification with Multi-Label Target Pt. 2: Creating a Web-App
  for message classification. The classification happens in a neat end-to-end sklearn pipeline.
  _The resources folder contains notebooks on bow / tfidf and on nlp pipelining from Udacity's DS nanondegree course._

- **price_prediction_ames_housing:** Supervised regression modelling to predict house prices. Comparision of ElasticNet and XGBoost. The focus of this project is on finding the right feature preprocessing and most of all on inspecting feature importances (among others with eli5 library).

- **recommender_systems_IBM-Watson:** More like a showcase of different approaches for creating a recommender system. (rank-based, content-based (with NLP part), user-based, Funk-SVD). 
  _Extensive resources section from Udacity's DS nanodegree course, also containing a complete recommender class._
 
- **survival_analysis_lifetimes:** Exploration of the functionality of Cameron Davidson's lifelines package. Goal is to construct survival functions / survival curves for customers (as a whole, in cohorts and individual). This is an alternative approach to churn analysis, based on the durations of customer relationship.

- **uplift_modelling_imbalanced_starbucks:** uplift modelling project dealing with very imbalanced target classes. The main point 
  was to experiment with the `imblearn` package and to create a pipeline that oversamples the minority target class with SMOTENC.
