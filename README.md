# Little project to understand rental price of real estate market in ukrainian city Kharkiv
**Resouce:** I parsed data from one of the largest real estate sites in Ukraine - [DimRia](https://dimriagroup.com).

In this project I used combination of asynchronous parsing and Selenium-based parsing to scrape the necessary data for next [EDA](https://github.com/elch1k/kharkiv_real_estate_rent_market/blob/main/rent_real_estate_project.ipynb) and machine learning predicton of real estate price.

The big problem of this project was data, which I didn't have much and tried to take it from every possible way, like dealing with text description to real estate announcement. After conducting [EDA](https://github.com/elch1k/kharkiv_real_estate_rent_market/blob/main/rent_real_estate_project.ipynb), I uncovered several interesting and significant patterns in the data. For example, I was able to visualize the distribution of real estate properties across different areas of Kharkiv and discovered notable differences in rental prices between these areas. The analysis revealed other valuable insights for potential renters, such as identifying key factors that influence rental prices and offering a comparison of average prices by city district. These findings could be particularly helpful for individuals looking to rent real estate in Kharkiv.

Then my goal was to build machine learning model and try quite accurate to predict this rental price of real estate in Kharkiv. So, classical variants of machine learning were used as predictive models. Their results are presented in the table below:
| Model                       | MSE          | MAE          | R-squared | R-squared (Train) | MAE (Train)   |
|-----------------------------|--------------|--------------|-----------|------------------|---------------|
| Random Forest               | 4.580877e+06 | 1606.498774  | 0.656982  | 0.939496         | 609.896002    |
| Gradient Boosting Regressor | 4.600255e+06 | 1614.994836  | 0.655531  | 0.791420         | 1208.242116   |
| XGBoost                     | 4.998876e+06 | 1651.411482  | 0.625682  | 0.996107         | 138.401950    |
| Linear Regression           | 5.073431e+06 | 1760.128605  | 0.620100  | 0.609799         | 1654.760582   |
| LightGBM                    | 5.484095e+06 | 1762.343387  | 0.589349  | 0.915263         | 732.378977    |
| ADA Boost                   | 5.837516e+06 | 1944.490796  | 0.562885  | 0.555730         | 1930.883255   |
| Linear SVR                  | 6.614721e+06 | 1912.023910  | 0.504687  | 0.455706         | 1895.603614   |
| Decision Tree               | 1.056401e+07 | 2153.120253  | 0.208963  | 0.999684         | 4.239326      |
| SVR                         | 1.390981e+07 | 2731.858771  | -0.041571 | -0.037534        | 2614.980070   |

From the results, we can see that I didn't get a relly amazing metrics on my test data and also I got overfitting with complex model like Random Forest and other boosting models. Despite this, we can roughly estimate the rental price. Here, among all the models, I would choose Linear Regression as it showed decent performance without significant overfitting. While it may not be as complex as the other models, its results were more consistent on both the training and test data.

Afterward, I also attempted to fine-tune the parameters of the XGBoost model, which led to a noticeably better result. With proper tuning, XGBoost can achieve solid performance:
> Mean Squared Error: 4463633.622977945
> R2 score: 0.6657614674096606

So if we choose maximum possible result from here we should use this tunning XGBoost with this parametrs - {'alpha': 0, 'colsample_bytree': 1.0, 'lambda': 1, 'learning_rate': 0.05, 'max_depth': 5, 'n_estimators': 150, 'subsample': 0.7}
